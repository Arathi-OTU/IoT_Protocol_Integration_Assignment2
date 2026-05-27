# Module 1 Assignment — Packet Analysis
## Task 4: Wire-Level Protocol Annotation

---

## 4.2 MQTT Packet Annotations

### CONNECT Packet

| Field | Offset (bytes) | Raw Hex | Decoded Value |
|-------|---------------|---------|---------------|
| Frame type + flags (byte 1) | 0 | `10` | Type=CONNECT (Command), flags=0001 |
| Remaining length (byte 2) | 1 | `45` | 69 bytes |
| Protocol name length | 2–3 | `00 04` | 4 |
| Protocol name | 4–7 | `4D 51 54 54` | "MQTT" |
| Protocol version | 8 | `04` | MQTT v3.1.1 (4) |
| Connect flags | 9 | `2c` | 0x2c, Will retain, QoS Level : At least once delivery (Acknowledge deliver), Will Flag  |
| Keep-alive | 10–11 | `00 3c` | 60 seconds |
| Client ID length | 12–13 | `00 1a` | 26 |
| Client ID | 14–… | `73 6d 61 72 74 66 61 63 74 6f 72 79 2d 70 75 62 6c 69 73 68 65 72 2d 30 30 31` | "smartfactory-publisher-001" |

**Connect Flags byte breakdown:**

| Bit | Name | Value | Meaning |
|-----|------|-------|---------|
| 7 | Username flag | 0 | Not set |
| 6 | Password flag | 0 | Not set |
| 5 | Will retain | 1 | Set |
| 4–3 | Will QoS | 01 | At least once delivery (Acknowledged deliver) (1) |
| 2 | Will flag | 1 | Set |
| 1 | Clean session | 0 | Not set |
| 0 | Reserved | 0 | — |

---

### QoS 1 PUBLISH Packet

| Field | Offset (bytes) | Raw Hex | Decoded Value |
|-------|---------------|---------|---------------|
| Fixed header byte 1 | 0 | `33` | Message Type: Publish Message, QoS Level : At least once delivery (Acknowledged deliver), Retain |
| Remaining length | 1 | `1e` | 30 bytes |
| Topic length | 2–3 | `00 14` | 20 |
| Topic string | 4–… | `66 61 63 74 6f 72 79 2f 6c 69 6e 65 31 2f 73 74 61 74 75 73` | "factory/line1/status" |
| Packet Identifier | … | `00 01` | 1 |
| Payload | … | `6f 6e 6c 69 6e 65` | "6f6e6c696e65" |

**Fixed header byte 1 bit expansion:**

| Bits 7–4 (packet type) | Bit 3 (DUP) | Bits 2–1 (QoS) | Bit 0 (RETAIN) |
|------------------------|-------------|----------------|----------------|
| `0011` = PUBLISH (3)  | `0` = No   | `01` = QoS 01   | `1` = Yes      |

---

### PUBACK Packet

| Field | Offset | Raw Hex | Decoded Value |
|-------|--------|---------|---------------|
| Fixed header | 0 | `40` | Message Type: Publish Ack |
| Remaining length | 1 | `02` | 2 bytes |
| Packet Identifier | 2–3 | `00 01` | 1 |

**Packet Identifier match:** PUBLISH PKT ID = 96 ; PUBACK PKT ID = 96 ; **Match? Yes**

---

## 4.3 CoAP Packet Annotations

### CON GET Request

```
Bytes: 42 01 57 56  a6 3b 60 57  66 ...
       [   Header   ] [  Token  ] [Options...]
```

| Field | Bits/Bytes | Raw Value | Decoded Value |
|-------|-----------|-----------|---------------|
| Version (bits 7–6) | 2 bits | `01` | 1 (always 1) |
| Type (bits 5–4) | 2 bits | `00` | Type = CON(0) |
| TKL (bits 3–0) | 4 bits | `0010` | Token length = 2 |
| Code (byte 1) | 8 bits | `01` | Code: GET (1) |
| Message ID (bytes 2–3) | 16 bits | `57 56` | 22358 |
| Token (bytes 4–TKL+3) | TKL bytes | `a6 3b` | Token: a63b |
| Option Delta | 4 bits | `0101` | Delta = 5, Option# = Type 11, Critical, Unsafe |
| Option Length | 4 bits | `0111` | 7 |
| Option Value | ___ bytes | `66 61 63 74 6f 72 79` | "factory" (Uri-Path) |

**Byte 0 full expansion:**

| Bit 7 | Bit 6 | Bit 5 | Bit 4 | Bit 3 | Bit 2 | Bit 1 | Bit 0 |
|-------|-------|-------|-------|-------|-------|-------|-------|
| Ver   | Ver   | T     | T     | TKL   | TKL   | TKL   | TKL   |
| `0`   | `1`   | `0`   | `0`   | `0`   | `0`   | `1`   | `0`   |

---

### ACK 2.05 Content Response

| Field | Bytes | Raw Hex | Decoded Value |
|-------|-------|---------|---------------|
| Fixed header byte 0 | 0 | `__` | Ver=01, T=10 (ACK), TKL=2 |
| Code byte 1 | 1 | `45` | 2.05 = Content |
| Message ID | 2–3 | `57 56` | 22358 (matches request? Yes) |
| Token | 4–… | `a6 3b` | a63b (matches request? Yes) |
| Option: Content-Format | … | `61 32` | Option# = 12, Elective, Safe |
| Payload Marker | … | `FF` | 0xFF |
| Payload | … | `7b 22 6c 69 6e 65 22 3a 20 ...` | "[Uri-Path:/ factory/line1/temperature]" |

---

### Observe Notification

| Field | Value |
|-------|-------|
| Observe option number | 4 |
| Observe sequence value | Uri-Path: temperature|
| Message type | Critical, Unsafe (CON) |
| Response code | 0b 74 65 6d 70 65 72 61 74 75 72 65 |

---

## 4.4 AMQP Frame Annotations

### basic.publish Method Frame

```
Bytes: 01  00 01  00 00 00 NN  [payload]  CE
       [T] [Ch] [Payload Sz] [.........] [End]
```

| Field | Bytes | Raw Hex | Decoded Value |
|-------|-------|---------|---------------|
| Frame Type | 0 | `__` | __ = Method |
| Channel | 1–2 | `__ __` | __ |
| Payload Size | 3–6 | `__ __ __ __` | ___ |
| Class ID | 7–8 | `__ __` | __ = basic (60) |
| Method ID | 9–10 | `__ __` | __ = basic.publish (40) |
| Reserved (ticket) | 11–12 | `00 00` | — |
| Exchange name length | 13 | `__` | __ |
| Exchange name | 14–… | `__ …` | "_______" |
| Routing key length | … | `__` | __ |
| Routing key | … | `__ …` | "_______" |
| Mandatory + Immediate | … | `__` | mandatory=_, immediate=_ |
| Frame End | last | `CE` | 0xCE ✓ |

---

### Content Header Frame

| Field | Bytes | Raw Hex | Decoded Value |
|-------|-------|---------|---------------|
| Frame Type | 0 | `02` | 2 = Header |
| Channel | 1–2 | `__ __` | __ |
| Payload Size | 3–6 | `__ __ __ __` | ___ |
| Class ID | 7–8 | `__ __` | 60 = basic |
| Weight | 9–10 | `00 00` | (unused) |
| Body Size | 11–18 | `__ … __` | ___ bytes |
| Property Flags | 19–20 | `__ __` | bits set: _______________ |
| delivery_mode | … | `__` | __ (1=transient, 2=persistent) |
| content_type length | … | `__` | __ |
| content_type | … | `__ …` | "_______" |
| Frame End | last | `CE` | 0xCE ✓ |

---

### Heartbeat Frame

| Field | Value |
|-------|-------|
| Frame Type | __ |
| Channel | __ |
| Payload Size | __ |
| Payload | _(empty)_ |
| Frame End | `CE` |

**Why is the Heartbeat payload empty?**

> _Your answer here (1–2 sentences)_

---

*Module 1 Assignment — Real-Time Data Analytics for IoT*
