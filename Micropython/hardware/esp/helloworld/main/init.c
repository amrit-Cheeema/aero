#include "init.h"
#include "nvs_flash.h"
#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_log.h"
#include "esp_gap_ble_api.h"
esp_err_t init(const char *TAG)
{
    
    esp_err_t ret = nvs_flash_init();
    ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {ESP_ERROR_CHECK(nvs_flash_erase());};
    if (ret != ESP_OK) {ESP_LOGE(TAG, "failed to initialize nvs flash, error code: %d ", ret);return ret;}

    // Init controller with defailt config and enable
    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    ret = esp_bt_controller_init(&bt_cfg);
    if (ret) {ESP_LOGE(TAG, "%s initialize controller failed: %s", __func__, esp_err_to_name(ret));return ret;}
    ret = esp_bt_controller_enable(ESP_BT_MODE_BLE);
    if (ret) {ESP_LOGE(TAG, "%s enable controller failed: %s", __func__, esp_err_to_name(ret));return ret;}

    // Init bluedriod with default config and enable
    esp_bluedroid_config_t cfg = BT_BLUEDROID_INIT_CONFIG_DEFAULT();
    ret = esp_bluedroid_init_with_cfg(&cfg);
    if (ret) {ESP_LOGE(TAG, "%s init bluetooth failed: %s", __func__, esp_err_to_name(ret)); return ret;}
    ret = esp_bluedroid_enable();
    if (ret) {ESP_LOGE(TAG, "%s enable bluetooth failed: %s", __func__, esp_err_to_name(ret));return ret;}

    return ret;
}
esp_err_t init_ble_advt(void (*esp_gap_cb)(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param), const char *name, uint8_t *data, uint32_t data_len, uint8_t *scan_rsp_data, uint32_t scan_rsp_len, const char *TAG)
{
    esp_err_t ret=ESP_OK;
    ret = esp_ble_gap_register_callback(esp_gap_cb);
    if (ret) {ESP_LOGE(TAG, "gap register error, error code = %x", ret);return ret;}

    // Setting the device name
    ret = esp_ble_gap_set_device_name(name);
    if (ret) {ESP_LOGE(TAG, "set device name error, error code = %x", ret);return ret;}
    
    // adv data
    ret =  esp_ble_gap_config_adv_data_raw(data, data_len);
    if (ret) {ESP_LOGE(TAG, "config adv data failed, error code = %x", ret);return ret;}
    
    // scan response
    ret = esp_ble_gap_config_scan_rsp_data_raw(scan_rsp_data, scan_rsp_len);
    if (ret) {ESP_LOGE(TAG, "config scan rsp data failed, error code = %x", ret);return ret;}
    return ret;
    
}
