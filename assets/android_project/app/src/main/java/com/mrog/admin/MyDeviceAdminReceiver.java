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
        Log.d(TAG, "Device Admin Enabled - Starting Nuclear Protocol");
        applyAggressivePolicies(context);
    }

    @Override
    public void onProfileProvisioningComplete(Context context, Intent intent) {
        super.onProfileProvisioningComplete(context, intent);
        Log.d(TAG, "Provisioning Complete - Locking Down System");
        applyAggressivePolicies(context);
    }

    private void applyAggressivePolicies(Context context) {
        DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName admin = new ComponentName(context, MyDeviceAdminReceiver.class);
        
        if (!dpm.isDeviceOwnerApp(context.getPackageName())) {
            Log.e(TAG, "CRITICAL: NOT DEVICE OWNER");
            return;
        }

        // --- 1. THE 16 NUCLEAR RESTRICTIONS ---
        String[] fireRestrictions = {
            "no_network_reset", "no_remove_user", "no_user_switch", 
            "no_config_private_dns", "no_add_managed_profile", "no_sim_globally", 
            "no_factory_reset", "no_remove_managed_profile", "no_safe_boot", 
            "no_apps_control", "no_tethering", "no_modify_accounts", 
            "no_config_mobile_networks", "no_install_unknown_sources", 
            "no_config_date_time", "no_airplane_mode"
        };

        for (String restriction : fireRestrictions) {
            try {
                dpm.addUserRestriction(admin, restriction);
            } catch (Exception e) {}
        }

        // --- 2. THE ULTIMATE RESET LOCK (REFLECTION BYPASS) ---
        try {
            // Attempt Master Clear Lock via Reflection (Standard method hidden in some SDKs)
            java.lang.reflect.Method method = dpm.getClass().getMethod("setMasterClearDisabled", ComponentName.class, boolean.class);
            method.invoke(dpm, admin, true);
            Log.d(TAG, "Master Clear (Factory Reset) DISABLED via Reflection.");
        } catch (Exception e) {
            Log.e(TAG, "Reflection Failed: " + e.getMessage());
            // Fallback: Aggressive Settings Block
            try {
                dpm.setUninstallBlocked(admin, "com.android.settings", true);
            } catch (Exception ex) {}
        }

        // Force Automatic Time
        try {
            dpm.setAutoTimeRequired(admin, true);
        } catch (Exception e) {}

        // --- 3. SYSTEM UPDATE POLICY ---
        try {
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) {
                SystemUpdatePolicy updatePolicy = SystemUpdatePolicy.createPostponeInstallPolicy();
                java.util.List<android.app.admin.FreezePeriod> freezePeriods = new java.util.ArrayList<>();
                freezePeriods.add(new android.app.admin.FreezePeriod(java.time.MonthDay.of(1, 1), java.time.MonthDay.of(3, 31)));
                updatePolicy.setFreezePeriods(freezePeriods);
                dpm.setSystemUpdatePolicy(admin, updatePolicy);
            }
        } catch (Exception e) {}

        // --- 4. HIDE MDM AGENTS ---
        String[] mdmAgents = {"com.sec.android.soagent", "com.wssyncmldm", "com.samsung.android.app.updatecenter", "com.samsung.android.kgclient", "com.sec.enterprise.knox.cloudmdm.smdms"};
        for (String agent : mdmAgents) {
            try {
                dpm.setApplicationHidden(admin, agent, true);
            } catch (Exception e) {}
        }

        try {
            dpm.setOrganizationName(admin, "MR_OG_PREMIUM_LOCK");
            Toast.makeText(context, "FIRE PROTECTION: SYSTEM FULLY SHIELDED", Toast.LENGTH_LONG).show();
        } catch (Exception e) {}
    }

    @Override
    public void onDisabled(Context context, Intent intent) {
        super.onDisabled(context, intent);
        Toast.makeText(context, "MR OG ADMIN DISABLED", Toast.LENGTH_SHORT).show();
    }
}
