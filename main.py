import os, json
from tqdm import tqdm
from yats.tree import buildTree
from yats import Scraper, BACKEND


def extract_dialogues(path: str, save_as: str):
    with open(path) as f:
        data = json.load(f)
    
    print("building conversation trees!")
    trees = []
    conversations = []
    for conversation in tqdm(data.values()):
        tree = buildTree(conversation)
        trees.append(tree)
    
    print("extracting conversations (root to leaf paths)!")
    for tree in tqdm(trees):
        for node in tree.values():
            if not node.isLeaf: continue
            conversation = node.tolist()
            if len(conversation) > 1:
                conversations.append(conversation)
    
    print("extracted", len(conversations), "conversations!")
    with open(save_as, "w", encoding="utf-8") as f:
        f.write(json.dumps(
            conversations, 
            ensure_ascii=False,
            indent=4,
        ))

def main(query, limit: int = 30):
    import json
    from tqdm import tqdm

    scraper = Scraper(BACKEND.snscrape)
    conversation_ids = [x["conversation_id"] for x in tqdm(
        scraper(query, do_backup=False, limit=limit), desc="top_level")]
    conversations = {}
    num_convos = len(conversation_ids)
    i, avg_len, total_len = 0, 0, 0
    pbar = tqdm(conversation_ids, desc=f"tot=0, avg=0")
    os.makedirs(query+"_backups", exist_ok=True)

    for conversation_id in pbar:
        i += 1    
        conversation = scraper.conversation(conversation_id, do_backup=True, 
                                            backup_path=f"{query}_backups/{conversation_id}.pkl")
        conversations[conversation_id] = conversation
        total_len += len(conversation)
        avg_len = total_len / i

        pbar.set_description(f"tot={total_len}, avg={avg_len:.2f}")
        print(f"checkpointing at {i}/{num_convos} conversations.")
        with open(f"{query}_{limit}_convo.json", "w") as f:
            f.write(json.dumps(
                conversations,
                ensure_ascii=False,
                indent=4,
            ))
        # json.dump(conversations, f, indent=4)

if __name__ == "__main__":
    # main("アイスクリームが好きです", 30)
    # main("मोदी समाचार", 30)
    # extract_dialogues("PyQt5_30_convo.json","PyQt5_extracted_dialogues.json")
    limit = 30
    query = "PyQt5"
    # main(query, limit)
    extract_dialogues(f"{query}_{limit}_convo.json", 
                      f"{query}_extracted_dialogues.json")