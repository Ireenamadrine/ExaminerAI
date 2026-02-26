# ExaminerAI Android App - Setup & Development Guide

## Overview
Your Android app now has:
- ✅ **Multi-page Navigation** with Jetpack Compose Navigation
- ✅ **Chaquopy Integration** for Python backend execution
- ✅ **5 Main Screens**: Home, Quiz, Progress, Settings, Control Panel
- ✅ **SQLCipher Database** for encrypted data storage
- ✅ **Python Service Layer** for seamless backend communication

## Project Structure

```
android-app/
├── app/src/main/java/com/example/examinerai/
│   ├── MainActivity.kt           # Entry point with NavController
│   ├── Navigation.kt             # Navigation routes and sealed class
│   ├── HomeScreen.kt             # Dashboard with action cards
│   ├── QuizScreen.kt             # Interactive quiz with Python integration
│   ├── ProgressScreen.kt         # View learning history & stats
│   ├── SettingsScreen.kt         # App configuration
│   ├── PythonService.kt          # Chaquopy wrapper for Python calls
│   ├── EngineClient.kt           # Backend communication (existing)
│   ├── AppDatabase.kt            # Room database with SQLCipher
│   ├── AppTheme.kt               # Material Design 3 theme
│   └── ... (other supporting files)
```

## Building the App

### Prerequisites
1. **Android Studio** (latest)
2. **Python 3.10 or 3.11** installed locally
3. **Gradle 8.2.2**
4. **Kotlin 1.9.22**

### Build Steps

```bash
# 1. Clone/Navigate to project
cd android-app

# 2. Clean build
./gradlew clean

# 3. Build the app
./gradlew buildDebug

# 4. Install on device/emulator
./gradlew installDebug
```

## Setting Up Chaquopy

### Step 1: Configure Python Path
Edit `app/build.gradle` and verify your Python path is correct:

```gradle
python {
    buildPython "C:\\Users\\harpr\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
}
```

**On macOS/Linux:**
```gradle
buildPython "/usr/local/bin/python3"
```

### Step 2: Bundle Python Modules
Place your Python code in: `src/main/assets/`

Create the directory structure:
```
app/src/main/assets/
├── core_intelligence/
│   ├── __init__.py
│   ├── engine.py
│   ├── cognitive.py
│   ├── state.py
│   ├── rewards.py
│   ├── q_learning.py
│   ├── rlvr.py
│   └── policy.py
├── examiner/
│   ├── __init__.py
│   ├── question_gen.py
│   └── evaluator.py
├── architecture/
│   ├── __init__.py
│   └── profiles.py
└── knowledge/
    └── (your knowledge base files)
```

### Step 3: Copy Python Files
Copy your Python backend to the assets folder:

```bash
# From workspace root
cp -r core_intelligence android-app/app/src/main/assets/
cp -r examiner android-app/app/src/main/assets/
cp -r architecture android-app/app/src/main/assets/
cp -r knowledge android-app/app/src/main/assets/
```

## Screen Descriptions

### 1. Home Screen (`HomeScreen.kt`)
- Dashboard with action cards
- License status display
- Quick navigation to Quiz, Progress, Settings
- Professional Material Design 3 UI

### 2. Quiz Screen (`QuizScreen.kt`)
- Interactive question display
- Confidence & weakness sliders
- Answer input field
- Real-time Python engine integration
- Feedback display with suggested actions
- Progress tracking

### 3. Progress Screen (`ProgressScreen.kt`)
- Statistics cards (Total, Average, Best scores)
- Interaction history from Room database
- Performance metrics
- Visual progress overview

### 4. Settings Screen (`SettingsScreen.kt`)
- Profile selection (calm_tutor / strict_examiner)
- Feature toggles (Web Access, LLM, Notifications, Auto-save)
- Appearance settings
- Data export
- Reset to defaults

### 5. Control Panel (`MainActivity.kt`)
- Original debug/admin interface
- Direct engine testing
- System configuration
- JSON request/response display

## Using the Python Service

The `PythonService` class provides easy access to your Python backend:

```kotlin
// In any Composable or Activity
val pythonService = PythonService.getInstance(context)

// Generate a question
val question = pythonService.generateQuestion("recursion")

// Process with learning engine
val result = pythonService.processWithEngine(
    topic = "recursion",
    confidence = 0.7,
    weakness = 0.3,
    lastAction = "ask_explanation",
    userFeedback = "confused",
    profileName = "calm_tutor"
)

// Get profile information
val profile = pythonService.getProfile("calm_tutor")

// Calculate reward
val reward = pythonService.calculateReward("correct", "ask_question")

// Build learning state
val state = pythonService.buildState("recursion", 0.7, 0.3, "explain")

// Log interaction
pythonService.logInteraction("recursion", stateJson, "explain", 0.85)
```

## Navigation Usage

Navigate between screens using `navController`:

```kotlin
// In any composable
navController.navigate(Screen.Quiz.route)
navController.navigate(Screen.Home.route)
navController.navigate(Screen.Progress.route)
navController.navigate(Screen.Settings.route)
navController.navigate(Screen.ControlPanel.route)

// Go back
navController.popBackStack()
```

## Database Integration

The app uses Room with SQLCipher for encrypted storage:

```kotlin
// Access database
val db = AppDatabase.get(context)

// Insert interaction
db.interactionDao().insert(
    InteractionEntity(
        topic = "recursion",
        action = "explain",
        reward = 0.85
    )
)

// Query all interactions
val interactions = db.interactionDao().getAll()
```

## Dependencies Added

```gradle
// Navigation
implementation "androidx.navigation:navigation-compose:2.7.7"

// Chaquopy Python
implementation "com.chaquo.python:python:3.11"

// Lifecycle
implementation "androidx.lifecycle:lifecycle-runtime-ktx:2.7.0"

// Other existing dependencies...
```

## Running on Device

### Option 1: Android Studio
1. Open project in Android Studio
2. Connect device via USB (enable Developer Mode)
3. Click "Run" button
4. Select your device

### Option 2: Command Line
```bash
./gradlew installDebug
adb shell am start -n com.example.examinerai/.MainActivity
```

## Troubleshooting

### Python Not Found
- Verify Python path in `build.gradle`
- Ensure Python version matches (3.10 or 3.11)
- Check `assets/` folder has all Python modules

### Navigation Issues
- Verify all Screen routes are defined in `Navigation.kt`
- Check NavHost start destination is set correctly
- Ensure NavController is passed to all composables

### Database Errors
- Check SQLCipher dependency is installed
- Verify Room annotations are processed (rebuild if needed)
- Check database file permissions

### Chaquopy Errors
- Check Python syntax (Python errors show in Logcat)
- Verify imports in Python modules (test locally first)
- Use Logcat to debug: `adb logcat | grep PythonService`

## Testing Python Integration

Test your Python functions locally before deploying:

```bash
# From project root
cd core_intelligence
python -c "from engine import core_step; print(core_step('recursion', 0.7, 0.3, '', 'correct'))"
```

## Next Steps

1. **Copy Python Files**: Move your Python backend to `assets/`
2. **Update Questions**: Modify question generation in `QuizScreen.kt`
3. **Customize UI**: Adjust colors/themes in `AppTheme.kt`
4. **Test Navigation**: Verify all screens work on device
5. **Debug Python**: Use Logcat to monitor Python execution
6. **Add Features**: Build additional screens as needed

## Architecture

```
MainActivity
    ↓
NavController + AppNavHost
    ↓
    ├─→ HomeScreen
    ├─→ QuizScreen (uses PythonService)
    ├─→ ProgressScreen (uses AppDatabase)
    ├─→ SettingsScreen
    └─→ ControlPanel
         ↓
    PythonService (Chaquopy)
         ↓
    Python Backend (core_intelligence, examiner, etc.)
         ↓
    Room Database (AppDatabase)
         ↓
    SQLCipher (Encrypted Storage)
```

## Key Features

- ✅ Multi-screen navigation with smooth transitions
- ✅ Real-time Python backend execution
- ✅ Encrypted database for security
- ✅ Material Design 3 UI
- ✅ Responsive and adaptive layout
- ✅ Progress tracking and statistics
- ✅ Learning profiles (calm_tutor, strict_examiner)
- ✅ Comprehensive settings panel

## Support

For issues with:
- **Chaquopy**: Check [Chaquopy Docs](https://chaquo.com/chaquopy/)
- **Jetpack Compose**: See [Compose Docs](https://developer.android.com/jetpack/compose)
- **Room Database**: Visit [Room Docs](https://developer.android.com/training/data-storage/room)

