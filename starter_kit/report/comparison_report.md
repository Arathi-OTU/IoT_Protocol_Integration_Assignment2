# Module 1 Assignment — Protocol Comparison Report

**Student Name:** ______Arathi Arathi_____________________
**Student ID:**   _______101057222____________________
**Date:**         ________28/06/2026___________________

---

## 5.1 QoS Comparison Results Table

> Run `pytest tests/mqtt/test_qos_loss.py -v -s` and paste the output table here.

| Protocol / QoS | Sent | Received | Lost (%) | Duplicates | Avg Latency (ms) |
|----------------|------|----------|----------|------------|-----------------|
| MQTT QoS 0 | 100|100 |0.00% |0 |267.4 |
| MQTT QoS 1 |100 |100 |0.00% |0 |170.6 |
| MQTT QoS 2 | 100|100 |0.00% |0 |730.1 |
| CoAP NON |100 |92 |8.00% |0 |0.7 |
| CoAP CON |100 |100 |0.00% |0 |0.8 |
| AMQP (confirms off) | | | | | |

**Analysis Questions:**

1. **Why does QoS 0 lose messages while QoS 1 and 2 do not?** *(2–3 sentences)*

   > QoS 0 can lose messages because it uses a "fire-and-forget" approach with no acknowledgement or retransmission mechanism. If packets are dropped during transmission, the sender does not resend them, leading to message loss(as seen in CoAP NON and commonly under packet loss). In contrast, QoS 1 and QoS 2 use acknowledgements and retransmission protocols, ensuring reliable delivery and preventing message loss even under network issues.

2. **QoS 1 may show duplicates. Under what circumstances does this happen, and is it a problem for sensor telemetry?** *(2–3 sentences)*

   > QoS 1 can produce duplicates when the sender does not receive acknowledgement for a published message (due to packet loss or delay) and therefore retransmits it. If the original message actually reached the broker but the acknowledgement was lost, the broker may receive the same message twice.
   > For sensor telemetry, this is usually acceptable because data is typically idempotent (e.g., temperature readings), but it can become an issue if duplicate readings affect calculations like counts, alerts, or billing. 

3. **QoS 2 has higher latency than QoS 1. What causes this, and when is the trade-off worth it?** *(2–3 sentences)*

   > QoS 2 has higher latency because it requires a four-step handshake(PUBLISH - PUBREC - PUBREL - PUBCOMP) to ensure "exactly once" delivery, adding extra round-trip communication compared to QoS 1. This additional acknowledgement cycle increases both delay and overhead.
   > This trade-off is worth it in scenarios where duplicate messages are unacceptable, such as financial transactions, critical control commands, or billing systems where even a single duplicate or loss could cause incorrect outcomes.

---

## 5.2 CoAP–HTTP Proxy Mapping

> Run `pytest tests/coap/test_proxy.py -v -s` and record the observed HTTP headers.

| HTTP Header | CoAP Option | Your Observed Value |
|-------------|-------------|---------------------|
| Content-Type | | |
| Cache-Control: max-age | | |
| ETag | | |
| Location | | |

---

## 5.3 Protocol Selection Recommendation

*(500–700 words. Justify each recommendation with specific technical evidence from your implementation and packet captures.)*

### Data Path Recommendations

| Data Path | Recommended Protocol | Justification |
|-----------|---------------------|---------------|
| Sensor → Cloud (high frequency, <100 ms latency) | | |
| Actuator commands (safety-critical, exactly-once) | | |
| Backend service-to-service routing | | |
| OTA firmware delivery to constrained MCU (Class 2) | | |

### Detailed Justification

> *(Write 500–700 words here. Each recommendation must cite specific evidence — e.g. measured latency values from Section 5.1, packet overhead observed in Task 4, or implementation complexity experienced in Tasks 1–3.)*

---

## 5.4 Reflection

### Technical Challenge

> One technical challenge was handling message matching and acknowledgments correctly in CoAP (especially CON requests and responses).
> At first, responses were occasionally being ignored or mismatched because the implementation wasn’t consistently using both the Message ID and Token together. This caused issues where an ACK or response could not be correctly linked back to the original request, especially under simulated loss or delay.
> It was resolved by strictly following CoAP’s design rules: using the Message ID only for transport-level reliability (ACK/timeout handling) and the Token for application-level request/response matching. Once the code was updated to separate these concerns properly and store pending requests in a lookup table keyed by Token + Message ID, the reliability and correctness issues were eliminated.

### Most Surprising Protocol Difference

> The most surprising difference is how stateful MQTT appears compared to CoAP in packet captures, even though both are used for lightweight IoT communication. MQTT runs over a persistent TCP connection, so in the capture you mostly see continuous stream behavior plus explicit control packets like PUBLISH and PUBACK tied to QoS, while CoAP over UDP shows discrete, self-contained messages (CON/NON with ACKs) that are easier to spot individually.
> What stood out most is that MQTT hides much of the “message structure” inside TCP, making application events less visually obvious in Wireshark/tshark, whereas CoAP packets look more transparent and directly traceable end-to-end.

### Most Complex Protocol to Implement

> CoAP was generally the more complex protocol to implement correctly.
> The main difficulty comes from its reliability model over UDP, which is not built in like TCP. You have to manually handle message types like CON, NON, ACK, and RST, along with retransmissions, timeouts, and duplicate detection. Getting the matching of Message IDs and tokens right (especially for request/response pairing and observing resources) adds extra state management that is easy to get wrong.
> In contrast, MQTT is simpler to implement because TCP already handles ordering and reliability, and the MQTT client library typically abstracts most of the protocol details like QoS flow, acknowledgments, and reconnections.

---

*Module 1 Assignment — Real-Time Data Analytics for IoT*
