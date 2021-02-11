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

pair<string, double> detect_language(fasttext::FastText& fastText, map<string, double> settings, wstring text)
{
    pair<string, double> lang_score = make_pair("other", 0.0);

    wstring sentence = remove_all_special(text);
	string utf8_sentence = wstring_to_utf8(sentence);
	istringstream utf8_stream(utf8_sentence);

	vector<pair<fasttext::real, string>> predictions;
	fastText.predictLine(utf8_stream, predictions, 1, settings["fasttext_threshold"]);

	if(predictions.size() > 0)
	{
		double probability = predictions[0].first;
		string lang_code = predictions[0].second.substr(9, 2);
        lang_score = make_pair(lang_code, probability);
	}

    return lang_score;
}

#endif