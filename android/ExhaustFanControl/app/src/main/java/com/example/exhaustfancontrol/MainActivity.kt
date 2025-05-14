package com.example.exhaustfancontrol

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import android.widget.Switch
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.example.exhaustfancontrol.models.ExhaustFan
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*
import javax.net.ssl.HttpsURLConnection
import java.io.OutputStreamWriter
import java.net.HttpURLConnection

class MainActivity : AppCompatActivity() {
    private val TAG = "MainActivity"
    
    // Backend server URL
    private val BASE_URL = "http://192.168.1.100:5000/api"
    
    // Device IDs
    private val DEVICE_ID_1 = "exhaust_fan_1"
    private val DEVICE_ID_2 = "exhaust_fan_2"
    
    // UI elements for Fan 1
    private lateinit var fan1StatusTextView: TextView
    private lateinit var fan1TempTextView: TextView
    private lateinit var fan1LastUpdatedTextView: TextView
    private lateinit var fan1Switch: Switch
    private lateinit var fan1ModeSwitch: Switch
    
    // UI elements for Fan 2
    private lateinit var fan2StatusTextView: TextView
    private lateinit var fan2TempTextView: TextView
    private lateinit var fan2LastUpdatedTextView: TextView
    private lateinit var fan2Switch: Switch
    private lateinit var fan2ModeSwitch: Switch
    
    // Swipe to refresh layout
    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    
    // Fan data
    private var fan1: ExhaustFan = ExhaustFan(DEVICE_ID_1, "Exhaust Fan 1", 0.0f, false, true, "")
    private var fan2: ExhaustFan = ExhaustFan(DEVICE_ID_2, "Exhaust Fan 2", 0.0f, false, true, "")
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize UI elements for Fan 1
        fan1StatusTextView = findViewById(R.id.fan1_status)
        fan1TempTextView = findViewById(R.id.fan1_temperature)
        fan1LastUpdatedTextView = findViewById(R.id.fan1_last_updated)
        fan1Switch = findViewById(R.id.fan1_switch)
        fan1ModeSwitch = findViewById(R.id.fan1_mode_switch)
        
        // Initialize UI elements for Fan 2
        fan2StatusTextView = findViewById(R.id.fan2_status)
        fan2TempTextView = findViewById(R.id.fan2_temperature)
        fan2LastUpdatedTextView = findViewById(R.id.fan2_last_updated)
        fan2Switch = findViewById(R.id.fan2_switch)
        fan2ModeSwitch = findViewById(R.id.fan2_mode_switch)
        
        // Initialize swipe to refresh layout
        swipeRefreshLayout = findViewById(R.id.swipe_refresh_layout)
        swipeRefreshLayout.setOnRefreshListener {
            refreshData()
        }
        
        // Set up Fan 1 switch listener
        fan1Switch.setOnCheckedChangeListener { _, isChecked ->
            if (fan1.autoMode) {
                Toast.makeText(this, "Cannot switch fan manually in AUTO mode", Toast.LENGTH_SHORT).show()
                fan1Switch.isChecked = fan1.fanStatus
                return@setOnCheckedChangeListener
            }
            controlFan(DEVICE_ID_1, isChecked)
        }
        
        // Set up Fan 1 mode switch listener
        fan1ModeSwitch.setOnCheckedChangeListener { _, isChecked ->
            controlMode(DEVICE_ID_1, isChecked)
        }
        
        // Set up Fan 2 switch listener
        fan2Switch.setOnCheckedChangeListener { _, isChecked ->
            if (fan2.autoMode) {
                Toast.makeText(this, "Cannot switch fan manually in AUTO mode", Toast.LENGTH_SHORT).show()
                fan2Switch.isChecked = fan2.fanStatus
                return@setOnCheckedChangeListener
            }
            controlFan(DEVICE_ID_2, isChecked)
        }
        
        // Set up Fan 2 mode switch listener
        fan2ModeSwitch.setOnCheckedChangeListener { _, isChecked ->
            controlMode(DEVICE_ID_2, isChecked)
        }
        
        // Initial data refresh
        refreshData()
    }
    
    /**
     * Refresh data for both fans
     */
    private fun refreshData() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // Fetch Fan 1 data
                fetchFanData(DEVICE_ID_1)
                
                // Fetch Fan 2 data
                fetchFanData(DEVICE_ID_2)
                
                withContext(Dispatchers.Main) {
                    // Update UI
                    updateUI()
                    
                    // Stop refresh animation
                    swipeRefreshLayout.isRefreshing = false
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error refreshing data: ${e.message}")
                
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Failed to refresh data: ${e.message}", Toast.LENGTH_SHORT).show()
                    swipeRefreshLayout.isRefreshing = false
                }
            }
        }
    }
    
    /**
     * Fetch data for a specific fan
     */
    private suspend fun fetchFanData(deviceId: String) {
        try {
            val url = URL("$BASE_URL/devices/$deviceId")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            
            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = connection.inputStream.bufferedReader().readText()
                val jsonObject = JSONObject(response)
                
                if (jsonObject.getBoolean("success")) {
                    val deviceJson = jsonObject.getJSONObject("device")
                    
                    val fan = ExhaustFan(
                        id = deviceJson.getString("id"),
                        name = deviceJson.getString("name"),
                        temperature = deviceJson.getDouble("last_temperature").toFloat(),
                        fanStatus = deviceJson.getBoolean("fan_status"),
                        autoMode = deviceJson.getBoolean("auto_mode"),
                        lastSeen = deviceJson.getString("last_seen")
                    )
                    
                    // Update appropriate fan object
                    if (deviceId == DEVICE_ID_1) {
                        fan1 = fan
                    } else {
                        fan2 = fan
                    }
                } else {
                    Log.e(TAG, "Error fetching fan data: ${jsonObject.getString("error")}")
                }
            } else {
                Log.e(TAG, "HTTP error: $responseCode")
            }
            
            connection.disconnect()
        } catch (e: Exception) {
            Log.e(TAG, "Exception fetching fan data: ${e.message}")
            throw e
        }
    }
    
    /**
     * Update the UI with current fan data
     */
    private fun updateUI() {
        // Update Fan 1 UI
        fan1TempTextView.text = getString(R.string.temperature_value, fan1.temperature)
        fan1StatusTextView.text = if (fan1.fanStatus) "ON" else "OFF"
        fan1StatusTextView.setTextColor(resources.getColor(
            if (fan1.fanStatus) R.color.fan_on else R.color.fan_off, 
            theme
        ))
        
        // Set switch without triggering listener
        fan1Switch.setOnCheckedChangeListener(null)
        fan1Switch.isChecked = fan1.fanStatus
        fan1Switch.setOnCheckedChangeListener { _, isChecked ->
            if (fan1.autoMode) {
                Toast.makeText(this, "Cannot switch fan manually in AUTO mode", Toast.LENGTH_SHORT).show()
                fan1Switch.isChecked = fan1.fanStatus
                return@setOnCheckedChangeListener
            }
            controlFan(DEVICE_ID_1, isChecked)
        }
        
        fan1ModeSwitch.setOnCheckedChangeListener(null)
        fan1ModeSwitch.isChecked = fan1.autoMode
        fan1ModeSwitch.setOnCheckedChangeListener { _, isChecked ->
            controlMode(DEVICE_ID_1, isChecked)
        }
        
        // Format and display last updated time
        try {
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.getDefault())
            inputFormat.timeZone = TimeZone.getTimeZone("UTC")
            val date = inputFormat.parse(fan1.lastSeen)
            
            val outputFormat = SimpleDateFormat("HH:mm:ss dd/MM/yyyy", Locale.getDefault())
            outputFormat.timeZone = TimeZone.getDefault()
            
            fan1LastUpdatedTextView.text = "Last updated: ${outputFormat.format(date)}"
        } catch (e: Exception) {
            fan1LastUpdatedTextView.text = "Last updated: ${fan1.lastSeen}"
        }
        
        // Update Fan 2 UI
        fan2TempTextView.text = getString(R.string.temperature_value, fan2.temperature)
        fan2StatusTextView.text = if (fan2.fanStatus) "ON" else "OFF"
        fan2StatusTextView.setTextColor(resources.getColor(
            if (fan2.fanStatus) R.color.fan_on else R.color.fan_off, 
            theme
        ))
        
        // Set switch without triggering listener
        fan2Switch.setOnCheckedChangeListener(null)
        fan2Switch.isChecked = fan2.fanStatus
        fan2Switch.setOnCheckedChangeListener { _, isChecked ->
            if (fan2.autoMode) {
                Toast.makeText(this, "Cannot switch fan manually in AUTO mode", Toast.LENGTH_SHORT).show()
                fan2Switch.isChecked = fan2.fanStatus
                return@setOnCheckedChangeListener
            }
            controlFan(DEVICE_ID_2, isChecked)
        }
        
        fan2ModeSwitch.setOnCheckedChangeListener(null)
        fan2ModeSwitch.isChecked = fan2.autoMode
        fan2ModeSwitch.setOnCheckedChangeListener { _, isChecked ->
            controlMode(DEVICE_ID_2, isChecked)
        }
        
        // Format and display last updated time
        try {
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.getDefault())
            inputFormat.timeZone = TimeZone.getTimeZone("UTC")
            val date = inputFormat.parse(fan2.lastSeen)
            
            val outputFormat = SimpleDateFormat("HH:mm:ss dd/MM/yyyy", Locale.getDefault())
            outputFormat.timeZone = TimeZone.getDefault()
            
            fan2LastUpdatedTextView.text = "Last updated: ${outputFormat.format(date)}"
        } catch (e: Exception) {
            fan2LastUpdatedTextView.text = "Last updated: ${fan2.lastSeen}"
        }
    }
    
    /**
     * Control fan status (ON/OFF)
     */
    private fun controlFan(deviceId: String, status: Boolean) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val url = URL("$BASE_URL/control/$deviceId/fan")
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json")
                connection.doOutput = true
                
                val jsonBody = JSONObject()
                jsonBody.put("status", status)
                jsonBody.put("source", "app")
                
                val outputStream = OutputStreamWriter(connection.outputStream)
                outputStream.write(jsonBody.toString())
                outputStream.flush()
                
                val responseCode = connection.responseCode
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    val response = connection.inputStream.bufferedReader().readText()
                    val jsonObject = JSONObject(response)
                    
                    if (jsonObject.getBoolean("success")) {
                        Log.d(TAG, "Fan control successful")
                        
                        // Update appropriate fan object
                        if (deviceId == DEVICE_ID_1) {
                            fan1.fanStatus = status
                        } else {
                            fan2.fanStatus = status
                        }
                        
                        withContext(Dispatchers.Main) {
                            updateUI()
                            Toast.makeText(this@MainActivity, "Fan ${if (status) "ON" else "OFF"}", Toast.LENGTH_SHORT).show()
                        }
                    } else {
                        Log.e(TAG, "Fan control failed: ${jsonObject.getString("error")}")
                        
                        withContext(Dispatchers.Main) {
                            Toast.makeText(this@MainActivity, "Control failed: ${jsonObject.getString("error")}", Toast.LENGTH_SHORT).show()
                            // Revert switch to previous state
                            refreshData()
                        }
                    }
                } else {
                    Log.e(TAG, "HTTP error: $responseCode")
                    
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "Control failed: HTTP $responseCode", Toast.LENGTH_SHORT).show()
                        // Revert switch to previous state
                        refreshData()
                    }
                }
                
                connection.disconnect()
            } catch (e: Exception) {
                Log.e(TAG, "Exception controlling fan: ${e.message}")
                
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Control failed: ${e.message}", Toast.LENGTH_SHORT).show()
                    // Revert switch to previous state
                    refreshData()
                }
            }
        }
    }
    
    /**
     * Control fan mode (AUTO/MANUAL)
     */
    private fun controlMode(deviceId: String, autoMode: Boolean) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val url = URL("$BASE_URL/control/$deviceId/mode")
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json")
                connection.doOutput = true
                
                val jsonBody = JSONObject()
                jsonBody.put("mode", autoMode)
                jsonBody.put("source", "app")
                
                val outputStream = OutputStreamWriter(connection.outputStream)
                outputStream.write(jsonBody.toString())
                outputStream.flush()
                
                val responseCode = connection.responseCode
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    val response = connection.inputStream.bufferedReader().readText()
                    val jsonObject = JSONObject(response)
                    
                    if (jsonObject.getBoolean("success")) {
                        Log.d(TAG, "Mode control successful")
                        
                        // Update appropriate fan object
                        if (deviceId == DEVICE_ID_1) {
                            fan1.autoMode = autoMode
                        } else {
                            fan2.autoMode = autoMode
                        }
                        
                        withContext(Dispatchers.Main) {
                            updateUI()
                            Toast.makeText(this@MainActivity, "Mode changed to ${if (autoMode) "AUTO" else "MANUAL"}", Toast.LENGTH_SHORT).show()
                        }
                    } else {
                        Log.e(TAG, "Mode control failed: ${jsonObject.getString("error")}")
                        
                        withContext(Dispatchers.Main) {
                            Toast.makeText(this@MainActivity, "Control failed: ${jsonObject.getString("error")}", Toast.LENGTH_SHORT).show()
                            // Revert switch to previous state
                            refreshData()
                        }
                    }
                } else {
                    Log.e(TAG, "HTTP error: $responseCode")
                    
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "Control failed: HTTP $responseCode", Toast.LENGTH_SHORT).show()
                        // Revert switch to previous state
                        refreshData()
                    }
                }
                
                connection.disconnect()
            } catch (e: Exception) {
                Log.e(TAG, "Exception controlling mode: ${e.message}")
                
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Control failed: ${e.message}", Toast.LENGTH_SHORT).show()
                    // Revert switch to previous state
                    refreshData()
                }
            }
        }
    }
    
    /**
     * Refresh button click handler
     */
    fun onRefreshClick(view: View) {
        refreshData()
    }
}