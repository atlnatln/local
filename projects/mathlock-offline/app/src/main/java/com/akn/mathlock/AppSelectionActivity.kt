package com.akn.mathlock

import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.graphics.drawable.Drawable
import android.os.Bundle
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.akn.mathlock.databinding.ActivityAppSelectionBinding
import com.akn.mathlock.databinding.ItemAppBinding
import com.akn.mathlock.util.PreferenceManager

data class AppInfo(
    val name: String,
    val packageName: String,
    val icon: Drawable,
    var isLocked: Boolean
)

class AppSelectionActivity : AppCompatActivity() {

    private lateinit var binding: ActivityAppSelectionBinding
    private lateinit var prefManager: PreferenceManager
    private val appList = mutableListOf<AppInfo>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAppSelectionBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefManager = PreferenceManager(this)

        binding.btnBack.setOnClickListener { finish() }

        loadApps()
        setupRecyclerView()
    }

    private fun loadApps() {
        val pm = packageManager
        val lockedApps = prefManager.getLockedApps()

        val installedApps = pm.getInstalledApplications(PackageManager.GET_META_DATA)
            .filter { app ->
                // Sadece başlatılabilir uygulamaları göster (system uygulamalarını da dahil edebilir tarayıcılar için)
                pm.getLaunchIntentForPackage(app.packageName) != null &&
                        app.packageName != packageName // Kendi uygulamamızı hariç tut
            }
            .sortedBy { pm.getApplicationLabel(it).toString().lowercase() }

        appList.clear()
        for (app in installedApps) {
            appList.add(
                AppInfo(
                    name = pm.getApplicationLabel(app).toString(),
                    packageName = app.packageName,
                    icon = pm.getApplicationIcon(app),
                    isLocked = lockedApps.contains(app.packageName)
                )
            )
        }
    }

    private fun setupRecyclerView() {
        binding.rvApps.layoutManager = LinearLayoutManager(this)
        binding.rvApps.adapter = AppAdapter(appList) { appInfo, isLocked ->
            prefManager.toggleAppLock(appInfo.packageName, isLocked)
        }
    }
}

class AppAdapter(
    private val apps: List<AppInfo>,
    private val onToggle: (AppInfo, Boolean) -> Unit
) : RecyclerView.Adapter<AppAdapter.ViewHolder>() {

    class ViewHolder(val binding: ItemAppBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemAppBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val app = apps[position]
        holder.binding.ivAppIcon.setImageDrawable(app.icon)
        holder.binding.tvAppName.text = app.name
        holder.binding.tvPackageName.text = app.packageName

        // Listener'ı geçici olarak kaldır, sonra tekrar ekle
        holder.binding.switchLock.setOnCheckedChangeListener(null)
        holder.binding.switchLock.isChecked = app.isLocked
        holder.binding.switchLock.setOnCheckedChangeListener { _, isChecked ->
            app.isLocked = isChecked
            onToggle(app, isChecked)
        }
    }

    override fun getItemCount() = apps.size
}
