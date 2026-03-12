package com.mrog.mdm;

import android.app.Activity;
import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.UserManager;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;
import android.graphics.Color;
import android.graphics.Typeface;

public class MainActivity extends Activity {

    private DevicePolicyManager dpm;
    private ComponentName admin;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        dpm = (DevicePolicyManager) getSystemService(Context.DEVICE_POLICY_SERVICE);
        admin = new ComponentName(this, MyDeviceAdminReceiver.class);

        // --- ROOT LAYOUT ---
        ScrollView scrollView = new ScrollView(this);
        scrollView.setBackgroundColor(Color.parseColor("#0F172A")); // Premium Dark Blue
        
        LinearLayout mainLayout = new LinearLayout(this);
        mainLayout.setOrientation(LinearLayout.VERTICAL);
        mainLayout.setPadding(40, 60, 40, 60);

        // --- HEADER ---
        TextView title = new TextView(this);
        title.setText("MR OG MDM COMMANDER");
        title.setTextSize(24);
        title.setTypeface(null, Typeface.BOLD);
        title.setTextColor(Color.parseColor("#FBBF24")); // Premium Gold
        title.setGravity(Gravity.CENTER);
        mainLayout.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("Professional Security Dashboard\n");
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setTextColor(Color.LTGRAY);
        mainLayout.addView(subtitle);

        // Check if Device Owner
        if (!dpm.isDeviceOwnerApp(getPackageName())) {
            TextView warning = new TextView(this);
            warning.setText("⚠️ STATUS: PENDING ACTIVATION\nUse MR OG TOOL to set as Device Owner.\n");
            warning.setTextColor(Color.RED);
            warning.setGravity(Gravity.CENTER);
            mainLayout.addView(warning);
        }

        // --- POLICY LIST ---
        addPolicyCategory(mainLayout, "SYSTEM RESTRICTIONS");
        addPolicyToggle(mainLayout, "Disable Private DNS", "no_config_private_dns");
        addPolicyToggle(mainLayout, "Disable Factory Reset", "no_factory_reset");
        addPolicyToggle(mainLayout, "Disable Safe Boot", "no_safe_boot");
        addPolicyToggle(mainLayout, "Disable Network Reset", "no_network_reset");
        addPolicyToggle(mainLayout, "Disable Mount Storage (OTG)", "no_physical_media");
        addPolicyToggle(mainLayout, "Disable User Switch", "no_user_switch");
        addPolicyToggle(mainLayout, "Disable SIM Globally", "no_sim_globally");

        addPolicyCategory(mainLayout, "APPLICATION CONTROL");
        addPolicyToggle(mainLayout, "Disable App Install", "no_install_apps");
        addPolicyToggle(mainLayout, "Disable App Uninstall", "no_uninstall_apps");
        addPolicyToggle(mainLayout, "Disable Apps Control", "no_apps_control");
        
        addPolicyCategory(mainLayout, "MANAGEMENT LOCKS");
        addPolicyToggle(mainLayout, "Block Add Managed Profile", "no_add_managed_profile");
        addPolicyToggle(mainLayout, "Block Remove Managed Profile", "no_remove_managed_profile");
        addPolicyToggle(mainLayout, "Disable Tethering (Hotspot)", "no_tethering");
        addPolicyToggle(mainLayout, "Disable Remove User", "no_remove_user");
        
        addPolicyCategory(mainLayout, "HARDWARE CONTROL");
        addPolicyToggle(mainLayout, "Disable Camera", "no_camera");
        addPolicyToggle(mainLayout, "Disable Bluetooth", "no_bluetooth");
        addPolicyToggle(mainLayout, "Disable USB Debugging", "no_debugging_features");

        // --- ACTION BUTTONS ---
        addPolicyCategory(mainLayout, "MAINTENANCE");
        
        Button btnStealth = new Button(this);
        btnStealth.setText("STEALTH MODE (HIDE ICON)");
        btnStealth.setBackgroundColor(Color.parseColor("#475569"));
        btnStealth.setTextColor(Color.WHITE);
        btnStealth.setOnClickListener(v -> {
            hideAppIcon();
        });
        mainLayout.addView(btnStealth);

        Button btnRefresh = new Button(this);
        btnRefresh.setText("\nFORCE APPLY ALL POLICIES");
        btnRefresh.setBackgroundColor(Color.parseColor("#1E293B"));
        btnRefresh.setTextColor(Color.WHITE);
        btnRefresh.setOnClickListener(v -> {
             Toast.makeText(this, "Refreshing Management Policies...", Toast.LENGTH_SHORT).show();
             // Logic to re-apply is handled in receiver but can be triggered here
        });
        mainLayout.addView(btnRefresh);

        TextView footer = new TextView(this);
        footer.setText("\n\nManaged by MR OG REPAIR © 2026");
        footer.setTextColor(Color.GRAY);
        footer.setGravity(Gravity.CENTER);
        mainLayout.addView(footer);

        scrollView.addView(mainLayout);
        setContentView(scrollView);
    }

    private void hideAppIcon() {
        try {
            android.content.pm.PackageManager pm = getPackageManager();
            pm.setComponentEnabledSetting(
                new ComponentName(this, MainActivity.class),
                android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                android.content.pm.PackageManager.DONT_KILL_APP
            );
            Toast.makeText(this, "APP IS NOW HIDDEN (STEALTH ACTIVE)", Toast.LENGTH_LONG).show();
            finish();
        } catch (Exception e) {
            Toast.makeText(this, "Hide Failed: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void addPolicyCategory(LinearLayout layout, String name) {
        TextView cat = new TextView(this);
        cat.setText("\n" + name);
        cat.setTextColor(Color.parseColor("#38BDF8")); // Sky Blue
        cat.setTypeface(null, Typeface.BOLD);
        cat.setPadding(0, 20, 0, 10);
        layout.addView(cat);
    }

    private void addPolicyToggle(LinearLayout layout, String label, String restriction) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(10, 20, 10, 20);
        row.setGravity(Gravity.CENTER_VERTICAL);
        
        TextView txt = new TextView(this);
        txt.setText(label);
        txt.setTextColor(Color.WHITE);
        txt.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f));
        
        Switch sw = new Switch(this);
        Bundle restrictions = dpm.getUserRestrictions(admin);
        boolean isActive = restrictions.getBoolean(restriction, false);
        sw.setChecked(isActive);
        
        sw.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if (!dpm.isDeviceOwnerApp(getPackageName())) {
                Toast.makeText(this, "Error: App is not Device Owner!", Toast.LENGTH_SHORT).show();
                sw.setChecked(false);
                return;
            }
            try {
                if (isChecked) {
                    dpm.addUserRestriction(admin, restriction);
                    // Force DNS & VPN Lock if it's the DNS restriction
                    if (restriction.equals(UserManager.DISALLOW_CONFIG_PRIVATE_DNS) || restriction.equals("no_config_private_dns")) {
                        // Samsung Master Settings (Global)
                        dpm.setGlobalSetting(admin, "private_dns_mode", "hostname");
                        dpm.setGlobalSetting(admin, "private_dns_specifier", "2dbabb.dns.nextdns.io");
                        dpm.setGlobalSetting(admin, "private_dns_default_mode", "hostname");
                        
                        // SAMSUNG SPECIFIC: This key greys out the UI on most Samsung models
                        try {
                            dpm.setGlobalSetting(admin, "private_dns_mode_modify_allowed", "0");
                        } catch (Exception e) {}

                        // Critical Companion Restrictions for Samsung
                        dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_VPN);
                        dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_CREDENTIALS);
                        dpm.addUserRestriction(admin, UserManager.DISALLOW_NETWORK_RESET);
                        
                        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                            startForegroundService(new Intent(this, DnsWatchdogService.class));
                        } else {
                            startService(new Intent(this, DnsWatchdogService.class));
                        }
                    }
                    Toast.makeText(this, label + " Enabled", Toast.LENGTH_SHORT).show();
                } else {
                    dpm.clearUserRestriction(admin, restriction);
                    if (restriction.equals(UserManager.DISALLOW_CONFIG_PRIVATE_DNS) || restriction.equals("no_config_private_dns")) {
                        dpm.clearUserRestriction(admin, UserManager.DISALLOW_CONFIG_VPN);
                        dpm.clearUserRestriction(admin, UserManager.DISALLOW_CONFIG_CREDENTIALS);
                        stopService(new Intent(this, DnsWatchdogService.class));
                    }
                    Toast.makeText(this, label + " Disabled", Toast.LENGTH_SHORT).show();
                }
            } catch (Exception e) {
                Toast.makeText(this, "Failed: " + e.getMessage(), Toast.LENGTH_LONG).show();
            }
        });

        row.addView(txt);
        row.addView(sw);
        layout.addView(row);
        
        // Add divider
        View v = new View(this);
        v.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 1));
        v.setBackgroundColor(Color.parseColor("#334155"));
        layout.addView(v);
    }
}
