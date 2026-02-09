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
        Log.d(TAG, "Device Admin Enabled");
        Toast.makeText(context, "MR OG ADMIN ACTIVATED", Toast.LENGTH_SHORT).show();

        // Initialize Policy Manager
        DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName adminComponent = new ComponentName(context, MyDeviceAdminReceiver.class);

        // --- 1. SET USER RESTRICTIONS (STRICTLY AS REQUESTED) ---
        Log.d(TAG, "Applying Restrictions...");

        // BLOCK FACTORY RESET FIRST (Double Force)
        setUserRestriction(dpm, adminComponent, "no_factory_reset", true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_FACTORY_RESET, true);

        // "KICK OUT" MODE (Blocks Settings/Fun)
        // Hii ndio code inayoweza kufanya settings zishindwe kufunguka au "Kutupa Nje"
        setUserRestriction(dpm, adminComponent, "no_fun", true);

        // Requested List:
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_NETWORK_RESET, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_REMOVE_USER, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_USER_SWITCH, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_CONFIG_PRIVATE_DNS, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_ADD_MANAGED_PROFILE, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_REMOVE_MANAGED_PROFILE, true);

        // "Disallow SIM Globally"
        setUserRestriction(dpm, adminComponent, "no_sim_globally", true);

        // Safety Extras
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_SAFE_BOOT, true);

        // CRITICAL ENFORCEMENT (IMMEDIATE ACTION)
        try {
            // Force Lock Screen Immediately to apply policies
            dpm.lockNow();
            Log.d(TAG, "Device Locked to enforce policy.");

            // Disable ADB (Optional - careful!)
            // dpm.setGlobalSetting(adminComponent,
            // android.provider.Settings.Global.ADB_ENABLED, "0");

            // Force Screen Timeout to stricter
            dpm.setMaximumTimeToLock(adminComponent, 30000L); // 30 sec

        } catch (Exception e) {
            Log.e(TAG, "Enforcement Error: " + e.getMessage());
        }

        // --- 2. MANAGE SYSTEM UPDATE POLICY (POSTPONE) ---
        try {
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.M) {
                try {
                    // REFLECTION TO BYPASS COMPILE ERROR
                    Class<?> policyClass = Class.forName("android.app.admin.SystemUpdatePolicy");
                    java.lang.reflect.Method createMethod = policyClass.getMethod("createPostponePolicy");
                    Object policy = createMethod.invoke(null);

                    dpm.setSystemUpdatePolicy(adminComponent, (SystemUpdatePolicy) policy);
                    Log.d(TAG, "Update Policy set to POSTPONE using Reflection");
                } catch (Exception e) {
                    Log.e(TAG, "Error creating postpone policy via reflection: " + e.getMessage());
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to set update policy: " + e.getMessage());
        }
    }

    private void setUserRestriction(DevicePolicyManager dpm, ComponentName admin, String key, boolean value) {
        try {
            if (value) {
                dpm.addUserRestriction(admin, key);
            } else {
                dpm.clearUserRestriction(admin, key);
            }
        } catch (SecurityException e) {
            Log.e(TAG, "Error setting restriction " + key + ": " + e.getMessage());
        }
    }

    @Override
    public void onDisabled(Context context, Intent intent) {
        super.onDisabled(context, intent);
        Toast.makeText(context, "MR OG ADMIN DISABLED", Toast.LENGTH_SHORT).show();
    }
}
