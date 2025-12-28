import json
from dataclasses import asdict

from global_state import state
from data_types.Flight import RawFlightResult, Availability


def save_raw_results_to_file(raw_results: list[RawFlightResult], filepath: str):
    serialised = [r.to_dict() for r in raw_results]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serialised, f, ensure_ascii=False, indent=2)

    state.logger.info(f"Saved {len(raw_results)} RawFlightResult items to {filepath}")

def load_raw_results_from_file(filepath: str) -> list[RawFlightResult]:
    with open(filepath, "r", encoding="utf-8") as f:
        raw_list = json.load(f)

    reconstructed: list[RawFlightResult] = []

    for item in raw_list:
        # Build Availability from dict fragment
        availability_fields = {
            "ID": item["ID"],
            "origin_airport": item["origin_airport"],
            "destination_airport": item["destination_airport"],
            "source": item["source"],
            "date": item["date"],
            "y_available": item["y_available"],
            "w_available": item["w_available"],
            "j_available": item["j_available"],
            "f_available": item["f_available"],
            "y_mileage": item["y_mileage"],
            "w_mileage": item["w_mileage"],
            "j_mileage": item["j_mileage"],
            "f_mileage": item["f_mileage"],
            "taxes_currency": item["taxes_currency"],
            "y_taxes": item["y_taxes"],
            "w_taxes": item["w_taxes"],
            "j_taxes": item["j_taxes"],
            "f_taxes": item["f_taxes"],
            "y_remaining_seats": item["y_remaining_seats"],
            "w_remaining_seats": item["w_remaining_seats"],
            "j_remaining_seats": item["j_remaining_seats"],
            "f_remaining_seats": item["f_remaining_seats"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "provider": item["provider"]
        }

        availability = Availability(**availability_fields)

        reconstructed.append(
            RawFlightResult(
                origin_region=item["origin_region"],
                destination_region=item["destination_region"],
                availability=availability
            )
        )

    state.logger.info(f"Loaded {len(reconstructed)} RawFlightResult items from {filepath}")
    return reconstructed

