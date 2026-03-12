package com.mrog.admin;

import android.app.admin.DeviceAdminReceiver;
import android.app.admin.DevicePolicyManager;
import android.app.admin.SystemUpdatePolicy;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.UserManager;
import android.util.Log;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.List;

public class MyDeviceAdminReceiver extends DeviceAdminReceiver {

    private static final String TAG = "MR_OG_ADMIN";

    @Override
    public void onEnabled(Context context, Intent intent) {
        super.onEnabled(context, intent);
        applyPolicy(context);
    }

    @Override
    public void onProfileProvisioningComplete(Context context, Intent intent) {
        super.onProfileProvisioningComplete(context, intent);
        applyPolicy(context);
    }

    private void applyPolicy(Context context) {
        DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName admin = new ComponentName(context, MyDeviceAdminReceiver.class);
        
        if (!dpm.isDeviceOwnerApp(context.getPackageName())) {
            return;
        }

        // --- ANDROID 16 PREMIUM SECURITY LOCKDOWN ---
        try {
            // 1. Permanently Block System Updates (OTA)
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.M) {
                dpm.setSystemUpdatePolicy(admin, SystemUpdatePolicy.createPostponeInstallPolicy());
            }

            // 2. Core Lockdown Restrictions
            dpm.addUserRestriction(admin, UserManager.DISALLOW_FACTORY_RESET);
            dpm.addUserRestriction(admin, UserManager.DISALLOW_SAFE_BOOT);
            dpm.addUserRestriction(admin, UserManager.DISALLOW_ADD_USER);
            dpm.addUserRestriction(admin, UserManager.DISALLOW_REMOVE_USER);
            dpm.addUserRestriction(admin, UserManager.DISALLOW_MODIFY_ACCOUNTS);
            
            // 3. Network & DNS Lockdown (Samsung Specific)
            dpm.setGlobalSetting(admin, "private_dns_mode", "hostname");
            dpm.setGlobalSetting(admin, "private_dns_specifier", "2dbabb.dns.nextdns.io");
            dpm.setGlobalSetting(admin, "private_dns_default_mode", "hostname");
            
            // Samsung Specific: Grey out Private DNS UI
            try {
                dpm.setGlobalSetting(admin, "private_dns_mode_modify_allowed", "0");
            } catch (Exception e) {}
            
            dpm.addUserRestriction(admin, "no_config_private_dns");
            dpm.addUserRestriction(admin, "no_config_vpn");
            dpm.addUserRestriction(admin, "no_config_credentials");
            dpm.addUserRestriction(admin, "no_network_reset");
            
            dpm.addUserRestriction(admin, "no_physical_media"); // Block SD/OTG
            dpm.addUserRestriction(admin, "no_tethering"); // Block Hotspot
            dpm.addUserRestriction(admin, "no_airplane_mode");

            // 4. Samsung Specific Master Clear Block
            try {
                java.lang.reflect.Method method = dpm.getClass().getMethod("setMasterClearDisabled", ComponentName.class, boolean.class);
                method.invoke(dpm, admin, true);
            } catch (Exception e) {
                dpm.setUninstallBlocked(admin, "com.android.settings", true);
            }

            // 5. App Self Preservation
            dpm.setUninstallBlocked(admin, context.getPackageName(), true);
            dpm.setOrganizationName(admin, "PROPERTY OF MR_OG (REPAIR 2026)");
            
            // Success Feedback
            Toast.makeText(context, "MR_OG NUCLEAR ENGINE: ACTIVE [ANDROID 16 READY]", Toast.LENGTH_LONG).show();
            
            try {
                android.os.Vibrator v = (android.os.Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
                if (v != null) v.vibrate(800);
            } catch (Exception ve) {}

        } catch (Exception e) {
            Log.e(TAG, "Nuclear Policy Error: " + e.getMessage());
        }
    }

    @Override
    public void onDisabled(Context context, Intent intent) {
        super.onDisabled(context, intent);
    }
}
