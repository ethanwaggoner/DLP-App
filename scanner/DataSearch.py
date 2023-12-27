from typing import List, Dict, Union, Tuple
import re


class DataSearch:
    def __init__(self, custom_search: List[Dict[str, Union[str, List[str]]]] = None):

        self.custom_search = custom_search if custom_search else []

    def _censor_match(self, match: str) -> str:

        if len(match) >= 4:
            return re.sub(r'(?<!\d)\d(?!\d)', '*', match[:-4]) + match[-4:]
        else:
            return match

    def _compile_regexes(self, regex: str, prefixes: List[str], suffixes: List[str]) -> List[re.Pattern]:

        if regex and prefixes and suffixes:
            return [re.compile(rf"{prefix}\s?{regex}\s?{suffix}") for prefix in prefixes for suffix in suffixes]
        else:
            return []

    def _find_matches(self, compiled_regexes: List[re.Pattern], data: str) -> List[str]:

        matches = []
        for compiled_regex in compiled_regexes:
            matches.extend(compiled_regex.findall(data))
        return matches

    def _get_compiled_regexes(self, custom):

        regex = custom.get("regex", "")
        prefixes = custom.get("prefixes", [""])
        suffixes = custom.get("suffixes", [""])
        return self._compile_regexes(regex, prefixes, suffixes)

    def _get_censored_matches(self, custom, matches):

        name = custom.get("name", "")
        return [(name, self._censor_match(match)) for match in matches]

    def search(self, data: str) -> List[Tuple[str, str]]:

        result_list = []
        for custom in self.custom_search:
            compiled_regexes = self._get_compiled_regexes(custom)
            matches = self._find_matches(compiled_regexes, data)
            censored_matches = self._get_censored_matches(custom, matches)
            result_list.extend(censored_matches)
        return result_list

