# HA_DEVICE_MANAGER

Mục đích của web app này là để hỗ trợ người dùng dễ hơn khi giao tiếp với Home Assistant, không cần phải hiểu về các thiết bị điện, không cần làm việc với các file yaml phức tạp.
Thay vào đó ta dùng 1 giao diện web để config các file con trong home assistant

**Tư tưởng chung**

Khi thêm 1 thiết bị mới, thì phải xem trong HA nó cần yêu cầu những tham số thế nào, qua đó, phải yêu càu người dùng nhập các trường đó trên web
Nếu muốn xóa đi thì tức là xóa thực thể đó trong HA

**ví dụ**

Thêm 1 công tắc MQTT
Thiết bị MQTT có 1 tham số là địa chỉ IP, ví dụ 192.168.1.32
Khi đó người dùng phải nhập vào API này, thì ajax sẽ làm nhiệm vụ connect vào API để lấy thông tin thiết bị xem netid của công tắc là gì, có bao nhiêu công tắc nhỏ trong đó, và lưu vào file switch.yaml theo dạng giống như dạng 1 công tắc mqtt trên HA

**Các chức năng của hệ thống**

Bao gồm:

- check config thì ở terminal ta dùng lệnh: hass --script check_config
- restart automation: http://localhost:8123/api/services/automation/reload 

Các lệnh khác thì gọi API tương tự

**Backup restore** 

Thì ta lưu các file trong thư mục ~/.homeassistant vào 1 file nén và tải về, muốn khôi phục thì giải nén ra

**Học lênh**

phải có 1 thiết bị broadlink

mỗi một ô input trong cửa sổ học lệnh sẽ tương ứng với 1 dịch vụ gọi đến server giao tiếp với broadlink hub để, khi hub nhận được tín hiệu sẽ trả về cho người dùng dòng lệnh tương ứng khi bấm vào điều khiển khi học lệnh. Chú ý mỗi 1 loại điều khiển có các cấu trúc khác nhau

**Automation**

Có các loài automation phổ biển: hẹn giờ, nhắc lịch, nhà vệ sinh, đồng bộ các công tắc
Phải tìm hiểu kĩ từng loại automation trong HA để có thể có những config phù hợp, phải hiểu được cơ chế hoạt động của automation

Trigger: tức là 1 sự thay đổi trạng thái nào đó để kích hoạt kịch bản:
Ví dụ: 

`trigger:
- platform: time
  at: 14:00
  `

thì khi đến 14h, kịch bản này đã được trigger lên

Tuy nhiên, khi trigger đã kích hoạt xong, thì cần điều kiện để có thể thực hiện hành động

Ví dụ:

`condition:
- condition: state
  entity_id: switch.den_tran
  state: on`


Túc là điều kiện đèn trần đang bật

Yếu tố cuối của 1 automation là action, là các thiết bị sẽ thực hiện hành động sau khi có kích hoạt và thỏa mãn điều kiện

Ví dụ:

`action:
- service: switch:turn_off
  data:
    entity_id: switch.den_tran
`

Tức là tắt đèn trần.

Kết hợp cả 3 cái trigger vào thì ta có 1 automation hoàn chỉnh: với ý nghĩa là vào lúc 2h, nếu đèn trần bật thì tắt nó đi

**chú ý**: trigger và action bắt buộc phải có, còn condition thì có thể có có thể không
### Cập nhật khi có bản smart Ir mới
Chạy file query_ircode.py để cập nhật lại mã ir

`
python query_ircode.py
`


