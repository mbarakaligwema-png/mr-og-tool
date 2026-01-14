# Mwongozo wa Kuunda Admin APK (Android Studio)

Hii `Android_Source` ni programu kamili ya Android ambayo ina features zote ulizoomba (Block Reset, Update, WIFI).

## Hatua za Kuunda APK:

### 1. Pakua na Install Android Studio
Kama huna Android Studio, ipakue hapa: [developer.android.com/studio](https://developer.android.com/studio)

### 2. Fungua Project
1.  Fungua Android Studio.
2.  Chagua **Open**.
3.  Nenda kwenye folder la `Android_Source` ulilo nalo hapa (`Documents\MR_OG_TOOL\Android_Source`).
4.  Subiri imalize "Gradle Sync" (inaweza kuchukua muda kidogo mara ya kwanza).

### 3. Badilisha Jina na Logo
*   **Kubadili Jina la App**:
    *   Fungua `app/src/main/res/values/strings.xml`.
    *   Badilisha `<string name="app_name">MR OG Bypasser</string>` (Weka jina lako hapo).

*   **Kubadili Logo**:
    *   Copy picha yako ya logo.
    *   Nenda `app/src/main/res/`.
    *   Right-click folder la `res` -> **New** -> **Image Asset**.
    *   Kwenye "Path", chagua logo yako.
    *   Bonyeza Next -> Finish.

### 4. Tengeneza APK
1.  Kwenye menu ya juu, bonyeza **Build** -> **Build Bundle(s) / APKs** -> **Build APK(s)**.
2.  Ikishamaliza, itakuambia "Build APK(s): APK(s) generated successfully".
3.  Bonyeza **locate** kuona faili lako la `.apk`.

---

## Jinsi ya Ku-Install na Ku-Set Admin (ADB)

Baada ya kupata APK yako, ili iweze kufanya kazi ya kuzuia Reset, lazima ui-set kama **Device Owner** kwa kutumia ADB (au tool yako ya MR OG):

`adb install jina_la_apk_yako.apk`

`adb shell dpm set-device-owner com.mrog.tool/.MyDeviceAdminReceiver`

*(Kumbuka: `com.mrog.tool` ni package name iliyopo kwenye `build.gradle`, unaweza kuibadilisha pia ukipenda).*
