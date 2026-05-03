from pathlib import Path
from faker import Faker
import json
import random
import uuid
from datetime import datetime, timezone

fake = Faker()

BASE_PATH = Path("landing_zone")

EVENT_TYPES = ["orders", "payments", "product_events", "customers"]


def write_json_event(event_type: str, event: dict) -> None:
    output_dir = BASE_PATH / event_type
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{event_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}.json"
    file_path = output_dir / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(event, f)


def generate_customer() -> dict:
    return {
        "customer_id": str(uuid.uuid4()),
        "email": fake.email(),
        "country": fake.country_code(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_order() -> dict:
    return {
        "order_id": str(uuid.uuid4()),
        "customer_id": str(uuid.uuid4()) if random.random() > 0.05 else None,
        "order_timestamp": datetime.now(timezone.utc).isoformat(),
        "currency": random.choice(["USD", "EUR", "GBP"]),
        "order_total": round(random.uniform(5, 500), 2),
        "order_status": random.choice(["created", "confirmed", "cancelled"]),
    }


def generate_payment() -> dict:
    return {
        "payment_id": str(uuid.uuid4()),
        "order_id": str(uuid.uuid4()),
        "payment_timestamp": datetime.now(timezone.utc).isoformat(),
        "payment_method": random.choice(["card", "paypal", "apple_pay", "bank_transfer"]),
        "payment_status": random.choice(["approved", "declined", "pending", "error"]),
        "amount": round(random.uniform(5, 500), 2),
    }


def generate_product_event() -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "customer_id": str(uuid.uuid4()) if random.random() > 0.1 else None,
        "product_id": str(uuid.uuid4()),
        "event_type": random.choice(["view", "add_to_cart", "remove_from_cart", "purchase"]),
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "device_type": random.choice(["desktop", "mobile", "tablet"]),
    }


GENERATORS = {
    "customers": generate_customer,
    "orders": generate_order,
    "payments": generate_payment,
    "product_events": generate_product_event,
}


def main(number_of_events: int = 100) -> None:
    generated_events = []

    for _ in range(number_of_events):
        event_type = random.choice(EVENT_TYPES)
        event = GENERATORS[event_type]()

        # Introduce late events (simulate delay)
        if random.random() < 0.1:
            event["event_timestamp"] = (
                datetime.now(timezone.utc)
                .replace(hour=random.randint(0, 23))
                .isoformat()
            )

        generated_events.append((event_type, event))

    # Introduce duplicates
    duplicates = random.sample(generated_events, k=int(0.1 * len(generated_events)))
    generated_events.extend(duplicates)

    # Introduce bad records
    for i in range(int(0.05 * len(generated_events))):
        event_type, event = generated_events[i]
        event["corrupted_field"] = {"unexpected": "structure"}

    # Write all events
    for event_type, event in generated_events:
        write_json_event(event_type, event)

    print(f"Generated {len(generated_events)} events (with duplicates & bad data)")

if __name__ == "__main__":
    main()