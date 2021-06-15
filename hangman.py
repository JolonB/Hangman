from collections import Counter

import numpy as np

def read_data():
    with open("data/words.txt", 'r') as data_file:
        data = data_file.read().split()

    # Get length of longest word from dataset
    longest_length = 0
    for word in data:
        longest_length = max(longest_length, len(word))

    # Create a dataset grouped by word length
    data_array = [0]*longest_length

    # Count the number of words in each group
    for word in data:
        data_array[len(word) - 1] += 1

    # Fill data_array with numpy arrays with spaces for each word
    # This means we can preallocate the array
    for index in range(longest_length):
        # Create an array that can hold the strings of the appropriate length
        data_array[index] = np.empty((data_array[index], 1), dtype="U{}".format(index+1))

    index_tracker = [0]*longest_length
    for word in data:
        # breakpoint()
        word_len = len(word)
        data_array[word_len-1][index_tracker[word_len-1]] = word
        index_tracker[word_len-1] += 1

    return data_array

def filter_words(word_list, keep_only=None, remove_only=None):
    def word_has(word, keep_only):
        # Check if the word contains the char in all of the specified indices
        for index in keep_only["indices"]:
            if word[index] != keep_only["char"]:
                return False
        return True

    if not (bool(keep_only) ^ bool(remove_only)):
        raise ValueError("Exactly one of keep_only or remove_only should be specified.")

    if keep_only: # ("char": 'c', "indices": [ind1, ind2, ...])
        word_list = [word for word in word_list if word_has(word[0], keep_only)]
    elif remove_only: # 'c'
        word_list = [word for word in word_list if remove_only not in word[0]]

    return np.array(word_list)

def get_most_common_letter_list(word_list):
    countable_string = "".join(np.concatenate(word_list))
    return Counter(countable_string)

def get_most_common_letter(word_list, asked_letters, weights=None):
    most_common_list = get_most_common_letter_list(word_list).most_common()
    
    start_index = 0
    letter_count = 0
    for index, most_common in enumerate(most_common_list):
        if most_common[0] not in asked_letters:
            if not weights:
                return most_common[0]
            start_index = index
            letter_count = most_common[1]
            break
    most_common_letter = weights.most_common()[-1] # least common letter
    for most_common in most_common_list[start_index:]:
        if most_common[1] == letter_count:
            if weights[most_common[0]] > weights[most_common_letter] and most_common[0] not in asked_letters:
                most_common_letter = most_common[0]
        else:
            break
    # Return most common letter once done
    return most_common_letter

    
def ask_for_letter(letter):
    response = input("Does the word contain the letter {}? ".format(letter))
    if response in 'Yy':
        response = input("Enter the positions of the letters (space delimited)\n> ")
        return [int(index) for index in response.split()]
    else:
        return []

def get_pretty_word(word_so_far):
    pretty_word = ""
    for letter in word_so_far:
        pretty_word += " {} ".format(letter if letter else '_')
    pretty_word += "\n"
    pretty_word += "".join(str(x).ljust(2).rjust(3) for x in range(len(word_so_far)))
    return pretty_word

if __name__ == "__main__":
    grouped_data = read_data()

    hidden_word = input("Enter the number of characters in your word OR enter a line of underscores.\nFor example, the word \"dog\" can be represented as either 3 or ___.\n> ")
    try:
        character_count = int(hidden_word)
    except ValueError:
        unique_input = list(set(hidden_word))
        if len(unique_input) == 1 and unique_input[0] == "_":
            character_count = len(hidden_word)
        else:
            raise ValueError("Input must be an integer or a line of underscores (one for each character in the word).")

    word_list = grouped_data[character_count-1]
    natural_weighting = get_most_common_letter_list(word_list)

    # TODO do some smart stuff
    # Count the most common letter in the current list
    # Ask the user about that letter
    # If they say no, remove_only='letter'
    # If they say yes, request the indices and keep_only=(letter, indices)
    # Repeat until man is hanged, or word is guessed

    asked_letters = set()

    max_guesses = 15

    word_so_far = [None]*character_count

    for guess in range(1000):
        print(get_pretty_word(word_so_far))

        most_common = get_most_common_letter(word_list, asked_letters, weights=natural_weighting)
        if not most_common:
            print("I can't guess your word. You might've made a mistake or it's just not in my dictionary.")
            break

        response = ask_for_letter(most_common)
        asked_letters.add(most_common)
        print(response)
        if response:
            word_list = filter_words(word_list, keep_only={'char':most_common, 'indices': response})
            for index in response:
                word_so_far[index] = most_common
        else:
            word_list = filter_words(word_list, remove_only=most_common)

        if len(word_list) == 0 or guess >= max_guesses:
            print("I ran out of guesses")
            break
        elif len(word_list) == 1:
            print("I think your word is \"{}\"".format(word_list[0][0]))
            break
