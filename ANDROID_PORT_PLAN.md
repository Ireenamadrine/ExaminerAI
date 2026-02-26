# Android Port Plan (Rust + JNI)

1) Create Rust crate `engine` with core_step, state build, Q-update, policy, profiles. Expose C ABI.
2) Target Android: `cargo ndk -t arm64-v8a -t armeabi-v7a -t x86_64 -o ./android-app/app/src/main/jniLibs build --release`.
3) In Android, load with `System.loadLibrary("engine")`; add JNI wrapper `EngineNative.kt` to map inputs/outputs.
4) Keep Python as reference; add parity tests comparing Rust vs Python outputs on sample states.
5) Do not ship Python in APK.
