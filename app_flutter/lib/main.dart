import 'package:flutter/material.dart';

import 'screens/camera_screen.dart';
import 'services/feedback_service.dart';
import 'services/settings_service.dart';
import 'services/tts_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final settingsService = SettingsService();
  await settingsService.load();
  final tts = TtsService();
  await tts.configure();
  runApp(ArgusApp(settingsService: settingsService, tts: tts));
}

class ArgusApp extends StatelessWidget {
  const ArgusApp({super.key, required this.settingsService, required this.tts});

  final SettingsService settingsService;
  final TtsService tts;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ARGUS IC',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0D47A1),
          primary: const Color(0xFF0D47A1),
          surface: const Color(0xFFF5FAFF),
        ),
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF5FAFF),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0D47A1),
          foregroundColor: Colors.white,
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: const Color(0xFF0D47A1),
            foregroundColor: Colors.white,
            minimumSize: const Size.fromHeight(56),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: const Color(0xFF0D47A1),
            minimumSize: const Size.fromHeight(56),
          ),
        ),
      ),
      home: CameraScreen(
        settingsService: settingsService,
        tts: tts,
        feedback: FeedbackService(tts: tts),
      ),
    );
  }
}
