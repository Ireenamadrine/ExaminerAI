# SQLCipher Setup (Android)

Dependency (Gradle):
implementation "net.zetetic:android-database-sqlcipher:4.5.4"

Open encrypted DB:
```
val passphrase = SQLiteDatabase.getBytes(secret.toCharArray())
val db = SQLiteDatabase.openOrCreateDatabase(dbFile, passphrase, null)
```

Key management:
- Derive secret from Android Keystore (device-bound, non-exportable).
- Never hardcode; never upload.
- Offer user data reset which deletes DB.

Scope:
- RLVR/interactions tables only.
- Web-check and logs remain transient.
