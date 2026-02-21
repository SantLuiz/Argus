import cv2
import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow.keras import layers, models

# ================================
# 1. Carregar e preparar o modelo EMNIST
# ================================

# Carregar dataset EMNIST (byclass = dígitos + letras maiúsculas/minúsculas)
(ds_train, ds_test), ds_info = tfds.load(
    'emnist/byclass',
    split=['train', 'test'],
    as_supervised=True,
    with_info=True
)

# Pré-processamento
def preprocess(image, label):
    image = tf.cast(image, tf.float32) / 255.0
    image = tf.expand_dims(image, -1)  # (28,28,1)
    return image, label

batch_size = 128
ds_train = ds_train.map(preprocess).shuffle(10000).batch(batch_size).prefetch(tf.data.AUTOTUNE)
ds_test = ds_test.map(preprocess).batch(batch_size).prefetch(tf.data.AUTOTUNE)

# Modelo CNN simples
model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(28,28,1)),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(ds_info.features['label'].num_classes, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Treinar rapidamente (para testes, poucas épocas)
print("Treinando modelo EMNIST...")
model.fit(ds_train, epochs=3, validation_data=ds_test)

# ================================
# 2. Carregar imagem da placa
# ================================

img = cv2.imread("placa.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Binarização (threshold adaptativo ajuda em iluminação desigual)
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 35, 15)

# Encontrar contornos (letras brancas em fundo preto)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Ordenar os contornos da esquerda para a direita
contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

# ================================
# 3. Extrair letras e classificar
# ================================
predicted_text = ""

for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if h > 20 and w > 10:  # ignorar ruídos pequenos
        roi = thresh[y:y+h, x:x+w]
        
        # Redimensionar para 28x28
        roi_resized = cv2.resize(roi, (28,28), interpolation=cv2.INTER_AREA)
        roi_resized = roi_resized.astype("float32") / 255.0
        roi_resized = np.expand_dims(roi_resized, axis=-1)  # (28,28,1)
        roi_resized = np.expand_dims(roi_resized, axis=0)   # (1,28,28,1)
        
        # Prever letra
        pred = model.predict(roi_resized, verbose=0)
        label = np.argmax(pred)
        
        # Mapear índice para caractere (EMNIST usa mapeamento NIST)
        mapping = ds_info.features['label'].names
        char = mapping[label]
        predicted_text += char

print("\n📌 Texto detectado na placa:", predicted_text)
