package com.example.exhaustfancontrol.models

/**
 * Data class representing an exhaust fan device
 * 
 * @property id Unique identifier for the device
 * @property name Display name of the device
 * @property temperature Current temperature reading
 * @property fanStatus Current fan status (true = ON, false = OFF)
 * @property autoMode Current operating mode (true = AUTO, false = MANUAL)
 * @property lastSeen Last time the device was seen (ISO format)
 */
data class ExhaustFan(
    val id: String,
    val name: String,
    val temperature: Float,
    var fanStatus: Boolean,
    var autoMode: Boolean,
    val lastSeen: String
)