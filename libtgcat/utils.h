#include <vector>
#include <map>
#include <fstream>
#include <locale>
#include <cctype>
#include <codecvt>

#ifndef UTILS_H
#define UTILS_H

using namespace std;

wstring char_to_wstring(const char* s)
{
    wstring_convert<codecvt_utf8<wchar_t>, wchar_t> converter;
    return converter.from_bytes(s);
}

wstring utf8_to_wstring(const string& str)
{
    wstring_convert<codecvt_utf8<wchar_t>> myconv;
    return myconv.from_bytes(str);
}

string wstring_to_utf8(const wstring& str)
{
    wstring_convert<codecvt_utf8<wchar_t>> myconv;
    return myconv.to_bytes(str);
}

struct TelegramChannel
{
    wstring title;
    wstring description;
    vector<wstring> posts;

    TelegramChannel(wstring title, wstring description, vector<wstring> posts)
    {
        this->title = title;
        this->description = description;
        this->posts = posts;
    }

    TelegramChannel(const char* title, const char* description, size_t post_count, const char** posts)
    {
        this->title = char_to_wstring(title);
        this->description = char_to_wstring(description);
        this->posts = vector<wstring>();

        for (size_t i = 0; i < post_count; i++)
        {
            this->posts.push_back(char_to_wstring(posts[i]));
        }
    }

    wstring get_all_text()
    {
        wstring result;
        result += this->title + L"\n";
        result += this->description + L"\n";

        for (size_t i = 0, post_count = posts.size(); i < post_count; i++)
        {
            result += this->posts[i] + L"\n";
        }

        return result;
    }
};

map<string, double> load_settings(const char* filename)
{
    map<string, double> settings;
    ifstream infile(filename);
    string key;
    double value;

    while(infile >> key >> value)
    {
        settings[key] = value;
    }

    return settings;
}

#endif