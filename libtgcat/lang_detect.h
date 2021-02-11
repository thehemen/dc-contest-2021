#include <vector>
#include <utility>
#include <map>
#include <set>
#include <locale>
#include <cctype>
#include <codecvt>
#include <algorithm>
#include <sstream>

#include "fasttext/fasttext.h"

#ifndef LANG_DETECT_H
#define LANG_DETECT_H

using namespace std;

wstring remove_all_special(wstring text)
{
    // Replace new line with spaces
    replace_if(text.begin(), text.end(), [] (const wchar_t& c) { return c == L'\n';}, L' ');

    // Replace punctutation with spaces
    replace_if(text.begin(), text.end(), [] (const wchar_t& c) { return iswpunct(c);}, L' ');

    // Remove all digit characters.
    text.erase(remove_if(text.begin(), text.end(), ::iswdigit), text.end());

    // Make all characters lower
    transform(text.begin(), text.end(), text.begin(), ::towlower);
    return text;
}

vector<wstring> tokenize(wstring text, wchar_t delimiter = L' ')
{
    wstring clean_text = remove_all_special(text);
    vector<wstring> words;
    size_t pos = clean_text.find(delimiter);
    size_t initialPos = 0;

    while(pos != wstring::npos)
    {
        words.push_back(clean_text.substr(initialPos, pos - initialPos));
        initialPos = pos + 1;
        pos = clean_text.find(L' ', initialPos);
    }

    words.push_back(clean_text.substr(initialPos, min(pos, clean_text.size()) - initialPos + 1));

    for(int i = words.size() - 1; i >= 0; --i)
    {
        if(words[i].size() == 0)
        {
            words.erase(words.begin() + i);
        }
    }

    return words;
}

map<wchar_t, set<size_t>> get_char_dict(vector<wstring> words)
{
    map<wchar_t, set<size_t>>  char_dict;

    for(size_t i = 0, word_num = words.size(); i < word_num; ++i)
    {
        for(wchar_t c: words[i])
        {
            if(char_dict.count(c) == 0)
            {
                char_dict[c] = set<size_t>();
            }

            char_dict[c].insert(i);
        }
    }

    return char_dict;
}

map<wchar_t, int> get_alphabet_dict(map<wchar_t, set<size_t>> char_dict, double threshold)
{
    map<wchar_t, int> alphabet_dict;
    int index_now = 0;
    int last_index = -1;

    for(const auto& [c, indices]: char_dict)
    {
        int c_int = (int)c;

        if(last_index == -1)
        {
            last_index = c_int;
        }
        else
        {
            int diff = c_int - last_index;
            double diff_value = (double)diff / (double)c_int;

            if(diff_value > threshold)
            {
                index_now++;
            }

            last_index = c_int;
        }

        alphabet_dict[c] = index_now;
    }

    return alphabet_dict;
}

map<size_t, int> get_word_dict(map<wchar_t, set<size_t>> char_dict, map<wchar_t, int> alphabet_dict)
{
    map<size_t, map<int, int>> raw_word_dict;

    for(const auto& [c, word_indices]: char_dict)
    {
        int alphabet_index = alphabet_dict[c];

        for(size_t word_index: word_indices)
        {
            if(raw_word_dict.count(word_index) == 0)
            {
                raw_word_dict[word_index] = map<int, int>();
            }

            if(raw_word_dict[word_index].count(alphabet_index) == 0)
            {
                raw_word_dict[word_index][alphabet_index] = 0;
            }

            raw_word_dict[word_index][alphabet_index]++;
        }
    }

    map<size_t, int> word_dict;

    for(const auto& [word_index, alphabet_index_dict]: raw_word_dict)
    {
        int most_frequent_index = -1;
        int max_counter = 0;

        for(const auto& [alphabet_index, counter]: alphabet_index_dict)
        {
            if(counter > max_counter)
            {
                max_counter = counter;
                most_frequent_index = alphabet_index;
            }
        }

        word_dict[word_index] = most_frequent_index;
    }

    return word_dict;
}

vector<wstring> get_sentences_by_lang(vector<wstring> words, map<size_t, int> word_dict)
{
    if(word_dict.size() == 0)
    {
        return vector<wstring>();
    }

    auto x = max_element(word_dict.begin(), word_dict.end(),
    	[](const pair<size_t, int>& p1, const pair<size_t, int>& p2)
    {
        return p1.second < p2.second;
    });

    int sentence_num = x->second + 1;
    vector<wstring> sentences(sentence_num);

    for(size_t word_index, word_num = words.size(); word_index < word_num; ++word_index)
    {
        sentences[word_dict[word_index]] += words[word_index] + L" ";
    }

    return sentences;
}

int get_total_length(vector<wstring> sentences)
{
    int total_len = 0;

    for(const auto& sentence: sentences)
    {
        total_len += sentence.size();
    }

    return total_len;
}

pair<string, double> detect_language(fasttext::FastText& fastText, map<string, double> settings, wstring text)
{
	auto words = tokenize(text);
	auto char_dict = get_char_dict(words);
	auto alphabet_dict = get_alphabet_dict(char_dict, settings["unicode_threshold"]);
	auto word_dict = get_word_dict(char_dict, alphabet_dict);
	auto sentences = get_sentences_by_lang(words, word_dict);
	int total_len = get_total_length(sentences);
	map<string, double> score_by_lang_code;

	for(const auto& sentence: sentences)
	{
		int sentence_len = sentence.size();
		double importance = (double)sentence_len / (double)total_len;
		string utf8_sentence = wstring_to_utf8(sentence);
		istringstream utf8_stream(utf8_sentence);

		vector<pair<fasttext::real, string>> predictions;
		fastText.predictLine(utf8_stream, predictions, 1, settings["fasttext_threshold"]);

		if(predictions.size() > 0)
		{
			double probability = predictions[0].first;
			string lang_code = predictions[0].second.substr(9, 2);

			if(score_by_lang_code.count(lang_code) == 0)
			{
				score_by_lang_code[lang_code] = 0.0;
			}

			score_by_lang_code[lang_code] += importance * probability;
		}
	}

	pair<string, double> best_language = make_pair("other", 0.0);

	for(const auto& [lang_code, score]: score_by_lang_code)
	{
		if(score > best_language.second)
		{
			best_language.second = score;
			best_language.first = lang_code;
		}
	}

    return best_language;
}

#endif