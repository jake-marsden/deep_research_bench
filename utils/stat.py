import os
import argparse
from utils import load_jsonl
from tqdm import tqdm

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    args = parser.parse_args()

    total_citations = 0
    total_valid_citations = 0
    total_num = 0
    total_usage = [0, 0]

    data = load_jsonl(args.input_path)

    for d in tqdm(data):
        if not d['citations']:
            continue
        
        # Count each citation URL once (citation-level evaluation)
        for c in d['citations_deduped'].values():
            if c['validate_error'] is not None:
                continue
            
            # Check if this citation has any valid validate_res entries
            has_valid_result = False
            is_citation_valid = False
            
            for _c in c['validate_res']:
                # Handle two possible formats:
                # Format 1: {'idx': 0, 'result': 'supported'}
                # Format 2: {'idx': 0, 'supported': 'explanation'} or {'idx': 0, 'unsupported': 'explanation'}
                
                if 'result' in _c:
                    result = _c['result']
                elif 'supported' in _c:
                    result = 'supported'
                elif 'unsupported' in _c:
                    result = 'unsupported'
                else:
                    result = 'unknown'
                
                if result != 'unknown':
                    has_valid_result = True
                    if result == 'supported':
                        is_citation_valid = True
                        break  # One supported claim makes the citation valid
            
            # Count the citation if it has at least one valid result
            if has_valid_result:
                total_citations += 1
                if is_citation_valid:
                    total_valid_citations += 1

        total_num += 1



    with open(args.output_path, 'w') as f:
        f.write(f'total_citations: {total_citations/total_num}\n')
        f.write(f'total_valid_citations: {total_valid_citations/total_num}\n')
        f.write(f'valid_rate: {total_valid_citations / total_citations}\n')