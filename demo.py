import json

from product_clarity import CoachState, next_step, record_answer, snapshot


def main() -> None:
    state = CoachState()
    print("Product Clarity Coach reference flow\n")
    while True:
        step = next_step(state)
        if step is None:
            break
        field_name, question = step
        print(question)
        answer = input("> ")
        record_answer(state, field_name, answer)
    print("\nProduct Clarity Snapshot")
    print(json.dumps(snapshot(state), indent=2))


if __name__ == "__main__":
    main()
