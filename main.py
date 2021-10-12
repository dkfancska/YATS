from yats import (check_requirements, get_version,
                  Scraper, BACKEND)


def main(query, limit: int = 30):
    import json
    from tqdm import tqdm

    scraper = Scraper(BACKEND.snscrape)
    conversation_ids = [x["conversation_id"] for x in tqdm(
        scraper(query, do_backup=False, limit=limit), desc="top_level")]
    conversations = {}
    i, avg_len, total_len = 0, 0, 0
    pbar = tqdm(conversation_ids, desc=f"tot=0, avg=0")
    for conversation_id in pbar:
        i += 1
        conversation = scraper.conversation(conversation_id)
        conversations[conversation_id] = conversation
        total_len += len(conversation)
        avg_len = total_len / i
        pbar.set_description(f"tot={total_len}, avg={avg_len:.2f}")

    with open(f"{query}_{limit}_convo.json", "w") as f:
        json.dump(conversations, f, indent=4)


if __name__ == "__main__":
    print("python version:", get_version())
    check_requirements()
    main("I like ice cream", 30)
