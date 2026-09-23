enum VoiceAction {
  analyzeNow,
  repeatDescription,
  stopAudio,
  increaseVolume,
  decreaseVolume,
  openSettings,
  backToCamera,
  enableDoorMode,
  disableDoorMode,
  muteAudio,
  unmuteAudio,
  help,
}

class VoiceCommand {
  const VoiceCommand(this.action);

  final VoiceAction action;
}
