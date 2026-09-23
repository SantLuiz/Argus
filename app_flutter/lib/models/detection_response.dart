class DetectionResponse {
  const DetectionResponse({
    required this.message,
    required this.audio,
    required this.detections,
    required this.processingTime,
    this.mode = 'exploration',
    this.depthSource = 'unknown',
  });

  factory DetectionResponse.fromJson(Map<String, dynamic> json) {
    return DetectionResponse(
      message: json['message'] as String? ?? '',
      audio: AudioPayload.fromJson(
          json['audio'] as Map<String, dynamic>? ?? const {}),
      detections: (json['detections'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(DetectionItem.fromJson)
          .toList(),
      processingTime: ProcessingTime.fromJson(
          json['processing_time_ms'] as Map<String, dynamic>? ?? const {}),
      mode: json['mode'] as String? ?? 'exploration',
      depthSource: json['depth_source'] as String? ?? 'unknown',
    );
  }

  final String message;
  final AudioPayload audio;
  final List<DetectionItem> detections;
  final ProcessingTime processingTime;
  final String mode;
  final String depthSource;
}

class AudioPayload {
  const AudioPayload(
      {required this.text, this.language = 'pt-BR', this.priority = 'normal'});

  factory AudioPayload.fromJson(Map<String, dynamic> json) {
    return AudioPayload(
      text: json['text'] as String? ?? '',
      language: json['language'] as String? ?? 'pt-BR',
      priority: json['priority'] as String? ?? 'normal',
    );
  }

  final String text;
  final String language;
  final String priority;
}

class DetectionItem {
  const DetectionItem({
    required this.className,
    required this.confidence,
    required this.zone,
    required this.depthLabel,
  });

  factory DetectionItem.fromJson(Map<String, dynamic> json) {
    final depth = json['depth'] as Map<String, dynamic>? ?? const {};
    return DetectionItem(
      className: json['label_pt'] as String? ??
          json['class_name'] as String? ??
          'objeto',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0,
      zone: json['zone'] as String? ?? 'centro',
      depthLabel: depth['label_pt'] as String? ?? 'nao estimado',
    );
  }

  final String className;
  final double confidence;
  final String zone;
  final String depthLabel;
}

class ProcessingTime {
  const ProcessingTime(
      {this.detectionMs = 0, this.depthMs = 0, this.totalMs = 0});

  factory ProcessingTime.fromJson(Map<String, dynamic> json) {
    return ProcessingTime(
      detectionMs: json['detection_ms'] as int? ?? 0,
      depthMs: json['depth_ms'] as int? ?? 0,
      totalMs: json['total_ms'] as int? ?? 0,
    );
  }

  final int detectionMs;
  final int depthMs;
  final int totalMs;
}
