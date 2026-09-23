import 'package:flutter_test/flutter_test.dart';
import 'package:argus_mobile/models/detection_response.dart';

void main() {
  test('parses backend detection response with audio priority', () {
    final response = DetectionResponse.fromJson({
      'message': 'Porta a frente.',
      'audio': {'text': 'Porta a frente.', 'priority': 'normal'},
      'detections': [
        {
          'class_name': 'porta',
          'confidence': 0.88,
          'zone': 'centro',
          'depth': {'label_pt': 'medio'},
        }
      ],
      'processing_time_ms': {
        'detection_ms': 10,
        'depth_ms': 20,
        'total_ms': 30
      },
      'depth_source': 'midas',
    });

    expect(response.message, 'Porta a frente.');
    expect(response.audio.priority, 'normal');
    expect(response.detections.single.depthLabel, 'medio');
    expect(response.processingTime.totalMs, 30);
    expect(response.depthSource, 'midas');
  });
}
