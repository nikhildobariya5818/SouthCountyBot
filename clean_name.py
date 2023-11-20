import re
import json
from typing import Dict, List, Tuple

class CleanName:
    """
        Clean all unnecessary prefix, suffix and keywords from name
    """
    KEYWORDS = ("%",'H/E',"\(", "\)","EST", "OF", "LE", "TRS", "TR", "Mr", "Mr\.", "Mrs", "Mrs\.", "Dr\.", "Doctor", "Esq\.", "ESQ", "JTRS", "PA","P\.A\.", "C/O", "GUARDIAN", "MINOR", "HUSBAND", "WIFE", )
    SUFFIXES = ("JR.", "JR", "SR. ", " SR.", "SR ", " SR", " IV", " IV ", " III", " III ", " II", " II ", " I", " I ",)
    STRIPS = (" ", "&", ",")

    def __init__(self, name: str) -> None:
        self.owner_name = name
        for val in self.STRIPS:
            name = str(name).strip(val)
        self.name = name.lower()
        self.full_name = ""
        self.first_name = ""
        self.last_name = ""
        self.suffix_name = ""
        self.names = []

    def _clear_keywords(self) -> None:
        """
            remove all specified unwanted keywords from raw name
        """
        for keyword in self.KEYWORDS:
            keyword = keyword.lower()
            pattern = r"\s{}\s".format(keyword)
            if self.name.startswith(keyword):
                pattern = r"\s*{}\s".format(keyword)
            elif self.name.endswith(keyword):
                pattern = r"\s{}\s*".format(keyword)

            if not keyword.isalpha():
                pattern = r"\s*{}\s*".format(keyword)
            self.name = re.sub(pattern, " ", self.name)
        self.name = self.name.strip().strip(",")

    @staticmethod
    def _remove_and_capture_suffix(name: str) -> Dict[str, str]:
        """
            capture suffix save it to object and remove from raw_name which needs to be processed
        """
        name_with_suffix = {"name": name}
        suffix_list = CleanName.SUFFIXES
        for suffix in suffix_list:
            suffix = suffix.lower()
            if suffix in name:
                pattern = r"{},".format(suffix)
                if suffix.startswith(" ") and re.search(pattern, name):
                    name_with_suffix.setdefault("suffix", suffix)
                    name = name.replace(suffix, "").strip().strip(",")

                if suffix.startswith(" ") and not name.endswith(suffix):
                    name_with_suffix.setdefault("suffix", "")
                else:
                    name_with_suffix.setdefault("suffix", suffix)
                    name = name.replace(suffix, "").strip().strip(",")
        name_with_suffix["name"] = name
        return name_with_suffix

    @staticmethod
    def _clean_name_for_comma(name) -> str:
        number_of_commas = name.count(",")
        name = name.replace(",", "", number_of_commas - 1).strip()
        name = name.split(",")
        splitted_name = list(map(str.strip, name))
        last_name = splitted_name.pop(0)
        first_name = splitted_name.pop(0)
        middle_name = " ".join(splitted_name[::])
        return f"{first_name} {middle_name} {last_name}"

    def _construct_full_name(self) -> str:
        """
            make full name using first, middle and last name together
        """
        return f"{str(self.first_name)} {str(self.middle_name)} {str(self.last_name)}"

    def _prepare_name_list(self) -> None:
        """
            prepare cleaned name list to be returned for use
        """
        name = {"owner_name": self.owner_name.upper(), "full_name": self.full_name.upper(),
                "first_name": self.first_name.upper(), "middle_name": self.middle_name.upper(),
                "last_name": self.last_name.upper(), "suffix_name": self.suffix_name.upper()}
        for key, value in name.items():
            name[key] = value.strip().upper()
        self.names.append(name)

    def _format_name_with_suffix(self, name: str) -> None:
        """
            format name i.e first name, middle name and last name with suffix name
        """
        name_and_suffix = self._remove_and_capture_suffix(name)
        self.suffix_name = name_and_suffix.get("suffix", "")
        _name = name_and_suffix.get("name")
        special_case = None
        if "," in _name:
            _name = self._clean_name_for_comma(_name)
        if " de " in _name:
            special_case = self._handle_special_case(_name)
        if not special_case:
            splitted_name = _name.split(" ")
            self.first_name = splitted_name[0]
            self.middle_name = " ".join(splitted_name[1:-1])
            self.last_name = splitted_name[-1] if len(splitted_name) > 1 else ""
            self.full_name = self._construct_full_name()
            self._prepare_name_list()

    def _handle_special_case(self, name) -> bool:
        _case_string = " de "
        first_name, middle_name, last_name = "", "", ""
        if re.search(_case_string, name.lower()):
            splitted_name = name.split(_case_string, 1)
            first_part = splitted_name[0].strip().split(" ")
            last_part = splitted_name[-1].strip().split(" ")
            first_name = first_part[0]
            if len(first_part) > 1:
                middle_names = first_part[1:]
                middle_name = " ".join(middle_names)
            last_name = f"{_case_string} {' '.join(last_part)}"
            self.first_name = first_name
            self.middle_name = middle_name
            self.last_name = last_name
            self.full_name = self._construct_full_name()
            self._prepare_name_list()
            return True


    def _clean_name(self) -> None:
        """
            clean normal names after clearing unwanted keywords
        """
        self._clear_keywords()
        self.names = []
        self._format_name_with_suffix(self.name)

    def _clean_name_for_and(self) -> None:
        """
            make cleaner names which contain "&"
        """
        self._clear_keywords()
        self.names = []
        name_list = list(map(str.strip, self.name.split("&")))
        for name in name_list:
            if name:
                self._format_name_with_suffix(name.strip())

    def _clean_name_for_wife(self) -> None:
        """
            make cleaner names which contain "&W"
        """
        self._clear_keywords()
        self.names = []
        wife_last_name = ""
        splitted_name = self.name.split("&w")
        husband_name, wife_name = list(map(str.strip, splitted_name))
        if husband_name:
            name_with_suffix = self._remove_and_capture_suffix(husband_name)
            self.suffix_name = name_with_suffix.get("suffix", "")
            _name = name_with_suffix.get("name")
            splitted_name = _name.split(" ")
            self.first_name = splitted_name[0]
            self.middle_name = " ".join(splitted_name[1:-1])
            self.last_name = splitted_name[-1]
            wife_last_name = splitted_name[-1]
            self.full_name = self._construct_full_name()
            self._prepare_name_list()
        if wife_name:
            name_with_suffix = self._remove_and_capture_suffix(wife_name)
            self.suffix_name = name_with_suffix.get("suffix", "")
            _name = name_with_suffix.get("name")
            splitted_name = _name.split(" ")
            self.first_name = splitted_name[0]
            self.middle_name = " ".join(splitted_name[1:])
            self.last_name = wife_last_name
            self.full_name = self._construct_full_name()
            self._prepare_name_list()

    def _clean_name_for_husband(self) -> None:
        """
            make cleaner names which contain "&H"
        """
        self._clear_keywords()
        self.names = []
        husband_last_name = ""
        splitted_name = self.name.split("&h")
        wife_name, husband_name = list(map(str.strip, splitted_name))
        if wife_name:
            name_with_suffix = self._remove_and_capture_suffix(wife_name)
            self.suffix_name = name_with_suffix.get("suffix", "")
            _name = name_with_suffix.get("name")
            splitted_name = _name.split(" ")
            self.first_name = splitted_name[0]
            self.middle_name = " ".join(splitted_name[1:-1])
            self.last_name = splitted_name[-1]
            husband_last_name = splitted_name[-1]
            self.full_name = self._construct_full_name()
            self._prepare_name_list()
        if husband_name:
            name_with_suffix = self._remove_and_capture_suffix(husband_name)
            self.suffix_name = name_with_suffix.get("suffix", "")
            _name = name_with_suffix.get("name")
            splitted_name = _name.split(" ")
            self.first_name = splitted_name[0]
            self.middle_name = " ".join(splitted_name[1:])
            self.last_name = husband_last_name
            self.full_name = self._construct_full_name()
            self._prepare_name_list()


    def get_cleaned_name(self) -> List:
        if "&w" in self.name:
            self._clean_name_for_wife()
        elif "&h" in self.name:
            self._clean_name_for_husband()
        elif "&" in self.name:
            self._clean_name_for_and()
        else:
            self._clean_name()
        return self.names

if __name__ == "__main__":
    names = [
            "Jr ALFREDO ANGEL & HILDA E ALVAREZ Sr.",
            "ADONNA M THAYER &", "KENNETH BONNARDEL",
            "JOSEPH R ROJAS",
            "CHARLES PACHECO &W CLARA",
            "FELIX A BLASINI &W",
            "VINCENT & MARIA MARANDO TRS",
            "BERNARD W SHRAGO &W SALLY J",
            "SHARON DEMARZIO TRS",
            "CHI-MAN CHANG &W KAM-HA",
            "ALBERTO J MILIAN &W MARIA R",
            "JOHN F FOSTER JR &W JORDANA",
            "ROBERT E BEASLEY &W DEBORAH D",
            "GLENN S KAPLAN &W",
            "JUDITH FEINMAN &H JOEL (TRS)",
            "ALESSANDRA DE ALMEIDA CACERES",
            "AMY AYAL-SHERIT &H SHAUL SHERIT", # TO ASK
            "SIMON FELDMAN &W DEBORAH AGAY",
            "PAUL A EDWARDS & GAYLE M KRAUSE",
            "GARY HIRSCH JTRS", # TO ASK: should JTRS be removed or not
            "STEVEN E MARCUS &W RUTH",
            "RAQUEL MAIDAN-SZYLLER &H GERMAN",
            "GLORIA I VALENCIA &H",
            "DIEGO MAURICIO SOSA VALENCIA LE",
            "EST OF IRMA DOSKOCZ (TRS)",
            "SHIRLEY B ATTIAS TRS &",
            "RODRIGUEZ, ANDRES JR", # ANDRES -> fname, RODRIGUEZ -> lname in this case, if comma is present
            "MARIANO G ISMAN",
            "ENRIQUEZ, STEPHEN C",
            "Paul Feldman, P.A.",
            "COX, G. ROBERT",
            "LAZO WEST BRICKELL INVESTMENTS",
            "BRADY LEE JONES III",
            # To validate
            "CHACIN, EDGAR J, SR.",
            # Need to handle this case too.
            "LILIA ALLEN (EST OF)",
            "JENKINS, JR., WOODROW C",
            "MARIN CUADRADO, LUIS ALFONSO",
            "HOYO MACIEL, JOSE",
            "Fishman, Gregory R, Esq.",
            "Marrero, Chamizo, Marcer Law LP.",
            "ROJAS DE PENA, FABIO A", # After "DE", including "DE" everything will be last name
            "VICTOR, QUEZADA, MR",
            "PINILLA, MARTIN A, II",
            "QUEZADA, VICTOR A, MR",
            "HERNANDEZ, ALBERTO A, Jr.",
            "EST OF AIDEE M BECERRIL DE TOBAR",
            "PAULA DE LA OSA",
            "PEDORA A & YASMINA B CORZON",
            "EDITH & GLORIA GODALES JTRS",
            "ELIAS ALVAREZ HERNANDEZ",
            "MISHRAY, JAIME F",
            "JULIO SANCHEN JR",
            "ALFRED F. ANDREU, P.A.",
            "CLARA DE LEON",
            "EDILBERTO BAEZ &W CARMEN &",
            "GORFINKEL, NESTOR, ESQ",
            "VERONICA NAGYMIHALY TR",
            "TOMS, G. E.",
            "CEDENO CAMACHO, RAFAEL EDURADO",
            ]
    alist = []
    # for name in names:
    #     c = CleanName(name)
    #     alist.append(c.get_cleaned_name())
    # import json
    # print(json.dumps(alist))
    c = CleanName("H Dillon Graham Iii Individually And As Personsona")
    print(json.dumps(c.get_cleaned_name()))