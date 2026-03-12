package com.mrog.mdm;

import android.app.admin.DeviceAdminReceiver;
import android.app.admin.DevicePolicyManager;
import android.app.admin.SystemUpdatePolicy;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.UserManager;
import android.util.Log;
import android.widget.Toast;

public class MyDeviceAdminReceiver extends DeviceAdminReceiver {

    private static final String TAG = "MR_OG_MDM";

    @Override
    public void onEnabled(Context context, Intent intent) {
        super.onEnabled(context, intent);
        applyPolicy(context);
        context.startService(new Intent(context, DnsWatchdogService.class));
    }

    @Override
    public void onProfileProvisioningComplete(Context context, Intent intent) {
        super.onProfileProvisioningComplete(context, intent);
        applyPolicy(context);
        context.startService(new Intent(context, DnsWatchdogService.class));
    }

    private void applyPolicy(Context context) {
        DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName admin = new ComponentName(context, MyDeviceAdminReceiver.class);
        
        if (!dpm.isDeviceOwnerApp(context.getPackageName())) {
            return;
        }

        // --- MR OG BRUTAL LOCK (ORIGINAL MASTER) ---
        try {
            // 1. Force Identity (Samsung UI Key)
            dpm.setOrganizationName(admin, "MR_OG MANAGEMENT SYSTEM");
            
            dpm.setGlobalSetting(admin, "private_dns_mode", "hostname");
            dpm.setGlobalSetting(admin, "private_dns_specifier", "2dbabb.dns.nextdns.io");
            dpm.setGlobalSetting(admin, "private_dns_default_mode", "hostname");

            // 2. APPLY BRUTAL RESTRICTIONS
            dpm.addUserRestriction(admin, "no_config_private_dns");
            dpm.addUserRestriction(admin, "no_config_vpn"); 
            dpm.addUserRestriction(admin, "no_config_credentials"); // Grey-out Specialist
            dpm.addUserRestriction(admin, "no_network_reset");
            dpm.addUserRestriction(admin, "no_factory_reset");
            dpm.addUserRestriction(admin, "no_safe_boot");
            
            // 3. FORCE OPEN HOTSPOT
            dpm.clearUserRestriction(admin, "no_config_tethering");
            dpm.clearUserRestriction(admin, "no_config_mobile_networks");
            
            dpm.setUninstallBlocked(admin, context.getPackageName(), true);

            Toast.makeText(context, "MR OG MASTER LOCK: ENABLED", Toast.LENGTH_LONG).show();

            // 4. Vibration Feedback
            try {
                android.os.Vibrator v = (android.os.Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
                if (v != null) v.vibrate(800);
            } catch (Exception ve) {}

        } catch (Exception e) {
            Log.e(TAG, "MDM Brutal Lock Error: " + e.getMessage());
        }
    }
}
