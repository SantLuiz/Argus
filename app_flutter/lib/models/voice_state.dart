enum VoiceInputMode {
  idle,
  passive,
  wakeCommand,
  pushToTalk,
  executing,
  suspended,
}

class VoiceState {
  const VoiceState({
    this.mode = VoiceInputMode.idle,
    this.listening = false,
    this.processing = false,
    this.transcription = '',
    this.showTranscription = false,
    this.message = '',
  });

  final VoiceInputMode mode;
  final bool listening;
  final bool processing;
  final String transcription;
  final bool showTranscription;
  final String message;

  bool get pushToTalkActive => mode == VoiceInputMode.pushToTalk && listening;

  VoiceState copyWith({
    VoiceInputMode? mode,
    bool? listening,
    bool? processing,
    String? transcription,
    bool? showTranscription,
    String? message,
  }) {
    return VoiceState(
      mode: mode ?? this.mode,
      listening: listening ?? this.listening,
      processing: processing ?? this.processing,
      transcription: transcription ?? this.transcription,
      showTranscription: showTranscription ?? this.showTranscription,
      message: message ?? this.message,
    );
  }
}
