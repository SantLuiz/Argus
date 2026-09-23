package com.example.argus_mobile

import android.content.Context
import android.media.AudioManager
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat

class MainActivity : FlutterActivity() {
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        io.flutter.plugin.common.MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            "argus/system_ui"
        ).setMethodCallHandler { call, result ->
            when (call.method) {
                "enterCameraMode" -> {
                    hideSystemBars()
                    result.success(null)
                }
                "exitCameraMode" -> {
                    showSystemBars()
                    result.success(null)
                }
                else -> result.notImplemented()
            }
        }
        io.flutter.plugin.common.MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            "argus/media_volume"
        ).setMethodCallHandler { call, result ->
            when (call.method) {
                "changeBySteps" -> {
                    val steps = call.argument<Int>("steps") ?: 0
                    result.success(changeMediaVolume(steps))
                }
                else -> result.notImplemented()
            }
        }
    }

    private fun hideSystemBars() {
        WindowCompat.setDecorFitsSystemWindows(window, false)
        val controller = WindowInsetsControllerCompat(window, window.decorView)
        controller.systemBarsBehavior =
            WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        controller.hide(WindowInsetsCompat.Type.systemBars())
    }

    private fun showSystemBars() {
        WindowCompat.setDecorFitsSystemWindows(window, true)
        WindowInsetsControllerCompat(window, window.decorView).show(WindowInsetsCompat.Type.systemBars())
    }

    private fun changeMediaVolume(steps: Int): Int {
        val audioManager = getSystemService(Context.AUDIO_SERVICE) as AudioManager
        val stream = AudioManager.STREAM_MUSIC
        val maxVolume = audioManager.getStreamMaxVolume(stream)
        val currentVolume = audioManager.getStreamVolume(stream)
        val nextVolume = (currentVolume + steps).coerceIn(0, maxVolume)
        audioManager.setStreamVolume(stream, nextVolume, AudioManager.FLAG_SHOW_UI)
        return ((nextVolume.toDouble() / maxVolume.toDouble()) * 100).toInt()
    }
}
