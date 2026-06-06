#ifndef BLE_INIT_H
#define BLE_INIT_H
#include "esp_bt.h"
#include "esp_gap_ble_api.h"
/**
 * @brief Runs initialization.
 * 
 * This function inits the nvs flash, BLE controller, and bluedriod.
 * 
 * @return ESP_OK if everthing is good, or returns error
 */
esp_err_t init(const char *TAG);

/**
 * @brief Runs BLE advertising initialization.
 * 
 * @param esp_gap_cb static viod callback that handles BLE events
 * @param name The name of the BLE device
 * @param data The advertising data for the BLE device
 * @param scan_rsp_data The scan response data for the BLE device
 * @return ESP_OK if everthing is good, or returns error
 */
esp_err_t init_ble_advt(
    void (*esp_gap_cb)(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param), 
    const char *name, 
    uint8_t *data,
    uint32_t data_len,
    uint8_t *scan_rsp_data, 
    uint32_t scan_rsp_len,
    const char *TAG);
#endif