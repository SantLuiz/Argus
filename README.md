#  Iniciação Científica  
## Sistema integrado de visão computacional e inteligência artificial para descrição do ambiente e sugestão de rotas para pessoas cegas e com baixa visão  

---

##  1. Descrição do Projeto  
O objetivo principal deste projeto é o desenvolvimento de uma **aplicação móvel** destinada a **auxiliar pessoas cegas e com baixa visão na locomoção por ambientes**.  

A solução proposta emprega **visão computacional** e **inteligência artificial (IA)** para:  
-  Identificar obstáculos presentes no caminho  
-  Interpretar comandos de voz  
-  Calcular trajetos mais seguros até um ponto de destino  
-  Responder de forma eficiente às solicitações dos usuários  

A proposta busca **proporcionar maior autonomia e segurança** para pessoas com deficiência visual, além de contribuir para a pesquisa em **acessibilidade** e **IA aplicada à inclusão social**.  


###  Tecnologias e Metodologias  
-  **Visão Computacional** → identificação e segmentação de obstáculos no ambiente  
-  **Aprendizado de Máquina (ML)** → detecção de padrões e otimização da navegação  
-  **Processamento de Linguagem Natural (PLN)** → interpretação de comandos de voz e interação intuitiva  

O modelo de IA será treinado utilizando **bases de dados pré-existentes**, contendo imagens anotadas e dados de profundidade, com foco em objetos e obstáculos comuns em ambientes **urbanos** e **internos**.  

###  Validação e Testes  
-  **Cenários controlados** → ambientes simulados para validação inicial  
-  **Condições reais** → testes em ruas, calçadas, corredores e áreas internas  
-  **Feedback de usuários** → ajustes contínuos para acessibilidade  

###  Impacto Esperado  
-  Maior **autonomia** e **segurança** para pessoas com deficiência visual  
-  Avanço das pesquisas em **visão computacional aplicada à acessibilidade**  
-  Contribuição para a **inclusão social** com soluções tecnológicas de impacto  

###  Equipe  
-  **Aluno de iniciação científica**: Luiz Santana e Welber Willian da Silva
-  **Professor Orientador**: Rogério da Costa Gião  
-  **Instituição**: UNIP - Universidade Paulista

---

## 2. Objetivo do Módulo Atual

A etapa atualmente implementada tem como finalidade:

- Capturar imagens do ambiente;
- Realizar tratamento e padronização dos dados visuais;
- Aplicar técnicas de detecção de objetos baseadas em redes neurais convolucionais;
- Estruturar as informações detectadas em formato compatível com o padrão COCO;
- Preparar os dados para futuras etapas de treinamento e inferência contextual.

Esta fase constitui a base computacional necessária para a construção de um sistema de assistência ambiental em tempo real.

---

## 3. Funcionalidades Implementadas

### 3.1 Processamento de Imagens

- Redimensionamento padronizado para entrada em redes neurais;
- Conversão de espaço de cor (BGR → RGB);
- Redução de ruído por filtro Gaussiano;
- Realce de contraste por CLAHE;
- Normalização de intensidade de pixels;
- Estruturação para armazenamento reprodutível.

### 3.2 Detecção de Objetos com YOLOv8

- Integração com modelo YOLOv8 (Ultralytics);
- Detecção de pessoas, obstáculos urbanos, mobiliário e veículos;
- Geração de *bounding boxes*;
- Armazenamento de resultados em formato JSON compatível com COCO;
- Salvamento de imagens anotadas para análise técnica.

### 3.3 Estruturação para Aprendizado Supervisionado

- Organização de imagens tratadas;
- Geração de anotações estruturadas;
- Conversão para tensores compatíveis com PyTorch;
- Preparação do pipeline para futura etapa de treinamento de CNN customizada.

---

## 4. Tecnologias Utilizadas

- Python 3.10+
- OpenCV
- NumPy
- scikit-image
- PyTorch
- Ultralytics YOLOv8
- Estrutura de anotações padrão COCO

---

## 6. Instalação e Execução

### 6.1 Clonagem do Repositório

- git clone https://github.com/SantLuiz/Argus.git
- cd Argus
- **Criação do Ambiente Virtual** python -m venv venv
- **Ativação Windows** venv\Scripts\activate
- **Ativação Linux/Mac** source venv/bin/activate
- **Instalando dependências** pip install -r requirements.txt

---

## 7. Procedimento de Uso (Fase Atual do Projeto)

Nesta etapa de desenvolvimento, o sistema encontra-se focado no módulo de captação, tratamento e detecção de objetos em imagens estáticas. O fluxo operacional segue a sequência descrita abaixo.

---

### 7.1 Preparação da Imagem de Entrada

1. Inserir uma imagem de teste no diretório raiz do projeto.
2. Recomenda-se utilizar imagens que representem cenários urbanos ou ambientes internos contendo possíveis obstáculos (ex.: pessoas, mobiliário, escadas, portas).

---

### 7.2 Execução do Pipeline de Pré-Processamento

O pré-processamento realiza:

- Redimensionamento padronizado;
- Conversão de espaço de cor;
- Redução de ruído (filtro Gaussiano);
- Realce de contraste (CLAHE);
- Normalização de intensidade dos pixels.

- **Execução processamento de imagem**  python preprocess.py
- A imagem tratada será armazenada no diretório - processed_images/
- **Execução Detecção de Objetos** python yolo_detection.py
- **Imagem anotada com detecções** yolo_output/detected.jpg
- **Arquivo JSON estruturado (formato COCO)** yolo_coco_annotations.json



