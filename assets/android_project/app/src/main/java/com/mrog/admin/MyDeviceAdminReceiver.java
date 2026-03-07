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

        // --- BLOCK RESETS & DNS CONFIG ---
        try {
            dpm.addUserRestriction(admin, UserManager.DISALLOW_FACTORY_RESET);
            dpm.addUserRestriction(admin, UserManager.DISALLOW_NETWORK_RESET);
            dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_PRIVATE_DNS);
        } catch (Exception e) {}

        try {
            java.lang.reflect.Method method = dpm.getClass().getMethod("setMasterClearDisabled", ComponentName.class, boolean.class);
            method.invoke(dpm, admin, true);
        } catch (Exception e) {
            try {
                dpm.setUninstallBlocked(admin, "com.android.settings", true);
            } catch (Exception ex) {}
        }

        try {
            dpm.setOrganizationName(admin, "MR_OG_PROTECTION");
        } catch (Exception e) {}
    }

    @Override
    public void onDisabled(Context context, Intent intent) {
        super.onDisabled(context, intent);
    }
}
