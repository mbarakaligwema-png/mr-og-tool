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
        ComponentName adminComponent = getWho(context);

        // --- 1. SET USER RESTRICTIONS ---
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_NETWORK_RESET, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_REMOVE_USER, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_USER_SWITCH, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_CONFIG_PRIVATE_DNS, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_ADD_MANAGED_PROFILE, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_FACTORY_RESET, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_REMOVE_MANAGED_PROFILE, true);

        // "Disallow SIM Globally" -> Closest standard is Mobile Networks config
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_CONFIG_MOBILE_NETWORKS, true);

        // Additional constraints often useful for lock
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_MOUNT_PHYSICAL_MEDIA, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_MODIFY_ACCOUNTS, true);
        setUserRestriction(dpm, adminComponent, UserManager.DISALLOW_INSTALL_UNKNOWN_SOURCES, true);

        // --- 2. MANAGE SYSTEM UPDATE POLICY ---
        try {
            // Set Update Policy to POSTPONE
            // This defers updates for 30 days automatically.
            dpm.setSystemUpdatePolicy(adminComponent, SystemUpdatePolicy.createPostponePolicy());

            // "Add New Period - Far Year" (Freeze Periods)
            // Note: Android only allows 90 days total freeze per year.
            // We set a freeze period for the maximum allowed range if needed, or rely on
            // POSTPONE.
            // Below helps prevent updates during specific ranges (e.g. holidays).
            // Example: Freeze from Jan 1 to Mar 1
            // List<SystemUpdatePolicy.FreezePeriod> freezePeriods = new ArrayList<>();
            // freezePeriods.add(new SystemUpdatePolicy.FreezePeriod(
            // java.time.MonthDay.of(1, 1),
            // java.time.MonthDay.of(3, 1)
            // ));
            // dpm.setSystemUpdatePolicy(adminComponent,
            // SystemUpdatePolicy.createPostponePolicy()); // Postpone is safer for generic
            // blocking

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
