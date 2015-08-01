# Author: Karl Stratos (stratos@cs.columbia.edu)
"""
This module is used to clean an English text file extracted using the Python
script by Giuseppe Attardi. You need to specify the path to the Stanford
tokenizer: e.g., path to the directory "stanford-corenlp-full-2014-08-27/".

Use it like: python3 clean_en.py [input.txt] [output.txt] > [log.txt]
"""

import argparse
import os
import subprocess

def clean1(input, lookahead, junk_length, output):
    """
    Preliminary cleaning before passing to the Stanford tokenizer.
    1. Removes "<...COMMAND...>" strings (len(COMMAND) < lookahead) like "<br>".
    2. Removes junk short (len(line) < junk_length) lines starting with special
       symbols, e.g., "!width=28|".
    3. Removes any non-ascii character.
    """
    BAD_STARTERS = {"|", "#", "!", "[["}  # Special starting symbols.

    with open(input, "r") as infile:
        with open(output, "w") as outfile:
            for line in infile:
                line = line[:-1]  # Get rid of the newline character.
                if not line: continue  # Empty.

                # Skip the line if it looks like "!width=28|", but not if it
                # looks like "!n the 20th century... [...long sentence]".
                if line[0] in BAD_STARTERS and len(line) < junk_length:
                    print(line)
                    continue

                # Go through each character of the line to remove <...> strings.
                i = 0
                while i < len(line):
                    if ord(line[i]) >= 128:  # Skip a non-ascii character.
                        i += 1
                        continue
                    if line[i] == "<":  # Found a "<".
                        br_string = "<"
                        matched = False
                        for j in range(i + 1, min(i + lookahead, len(line))):
                             br_string += line[j]
                             if line[j] == ">":
                                 matched = True
                                 break

                        if matched:  # Have a matching ">".
                            print(br_string)  # Won't write this!
                            i += len(br_string)
                            continue
                        # If no matching ">", pretend we never found "<".
                    outfile.write(line[i])
                    i += 1
                outfile.write("\n")

def purify(input, purity, output):
    """
    Discards sentences where the portion of alphabetic characters among
    non-white characters falls below (<) the purity threshold.
    """
    with open(input, "r") as infile:
        with open(output, "w") as outfile:
            for line in infile:
                num_nonwhite_char = 0
                num_alpha = 0
                for char in line:
                    if char.isspace(): continue  # Ignore white characters.
                    num_nonwhite_char += 1
                    if char.isalpha():
                        num_alpha += 1
                if float(num_alpha) / num_nonwhite_char < purity:  # Unpure!
                    print(line[:-1])
                    continue
                outfile.write(line)

def main(args):
    """Main procedure"""
    tokenizer_path = "../../../third_party/stanford-corenlp-full-2014-08-27"
    assert(os.path.isdir(tokenizer_path))

    # Do initial cleaning.
    input_clean1 = args.input + "__clean1"
    clean1(args.input, args.lookahead, args.junk_length, input_clean1)

    # Run Stanford tokenizer.
    input_clean1_tok = input_clean1 + "__tok"
    tokenizer_command = "java -cp '{0}/*' edu.stanford.nlp.process.DocumentPreprocessor {1} > {2}".format(tokenizer_path, input_clean1, input_clean1_tok)
    subprocess.call(tokenizer_command, shell=True)

    # Sort and remove duplicate sentences.
    input_clean1_tok_nodup = input_clean1_tok + "__nodup"
    sort_delete_command = "cat {0} | sort | uniq > {1}".format(
        input_clean1_tok, input_clean1_tok_nodup)
    subprocess.call(sort_delete_command, shell=True)

    # Finally, only keep sentences whose non-white characters are mostly
    # alphabetic.
    purify(input_clean1_tok_nodup, args.purity, args.output)

    # Remove intermediate files.
    subprocess.call(["rm", "-rf", input_clean1])
    subprocess.call(["rm", "-rf", input_clean1_tok])
    subprocess.call(["rm", "-rf", input_clean1_tok_nodup])

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input", type=str, help="original wiki text file")
    argparser.add_argument("output", type=str, help="cleaned text")
    argparser.add_argument("--lookahead", type=int, default=80, help="amount "
                           "to look ahead for removing angled brackets "
                           "(default: %(default)d)")
    argparser.add_argument("--junk_length", type=int, default=150, help="a line"
                           " starting with a special symbol is considered junk "
                           "if its length is < this (default: %(default)d)")
    argparser.add_argument("--purity", type=float, default=0.6, help="a line "
                           "needs to have >= this portion alphabetic (excluding"
                           " white spaces) (default: %(default)f)")
    parsed_args = argparser.parse_args()
    main(parsed_args)
