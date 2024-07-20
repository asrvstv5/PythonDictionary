import tkinter as tk
from tkinter import messagebox, ttk
import requests
from bs4 import BeautifulSoup
import os
from requests.exceptions import SSLError
import urllib3
import certifi

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DictionaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dictionary App")
        self.dictionary_file = "dictionary.txt"
        self.error_log_file = "error_log.txt"
        self.initialize_files()
        self.create_widgets()

    def initialize_files(self):
        """Initialize necessary files if they do not exist."""
        self._create_file_if_not_exists(self.dictionary_file)
        self._create_file_if_not_exists(self.error_log_file)

    def _create_file_if_not_exists(self, filename):
        """Create a file if it does not already exist."""
        if not os.path.exists(filename):
            with open(filename, 'w') as file:
                pass

    def create_widgets(self):
        """Create and place all the frames."""
        self.search_frame = SearchFrame(self.root, self.search_word)
        self.search_frame.pack(pady=10)

        self.result_frame = ResultFrame(self.root)
        self.result_frame.pack(pady=10)

        self.add_word_frame = AddWordFrame(self.root, self.add_word)
        self.add_word_frame.pack(pady=10)

        self.display_words_frame = DisplayWordsFrame(self.root)
        self.display_words_frame.pack(pady=10)

        self.history_frame = HistoryFrame(self.root)
        self.history_frame.pack(pady=10)

        self.load_saved_words()

    def search_word(self, word):
        """Search for a word and update the result frame."""
        if not word:
            self._show_message("Error", "Please enter a word to search.")
            return
        try:
            meaning, usage, synonyms, antonyms = self.fetch_word_data(word)
            self.result_frame.display_word_data(meaning, usage, synonyms, antonyms)
            self.history_frame.add_to_history(word)
        except Exception as e:
            self._show_message("Error", f"An error occurred: {str(e)}")
            self.log_error(e)

    def fetch_word_data(self, word):
        """Fetch data for a word from the online dictionary."""
        url = f"https://www.dictionary.com/browse/{word}"
        response = requests.get(url, verify=certifi.where())
        soup = BeautifulSoup(response.content, "html.parser")

        meaning = "No meaning found."
        # Extracting the first definition from the ol tag with data-type='definition-content-list'
        definition_list = soup.find('ol', {'data-type': 'definition-content-list'})
        if definition_list:
            meanings = [li.text for li in definition_list.find_all('li')]
            meaning = "\n -".join(meanings) if meanings else "No meaning found."
        else:
            meaning = "No meaning found."

        meaning = "-" + meaning
        # usage = self._extract_text(soup, "css-1tw6lmu e1q3nk1v3", "No usage examples found.")
        usage = self.extract_usage(soup)
        # Extract synonyms from the meaning text
        synonyms = self.extract_synonyms(meaning)
        antonyms = self.extract_antonyms(meaning)

        return meaning, usage, synonyms, antonyms

    def extract_usage(self, soup):
        usage_section = soup.find('section', {'data-type': 'example-sentences-module'})
        if usage_section:
            examples = usage_section.find_all('div')
            usage_examples = [div.find('p').text for div in examples if div.find('p')]
            return "\n-".join(usage_examples) if usage_examples else "No usage examples found."
        else:
            return "No usage examples found."

    def extract_synonyms(self, text):
        """Extract synonyms from the text based on the 'Synonyms:' keyword."""
        start_index = text.find("Synonyms:")
        if start_index == -1:
            return "No synonyms found."
        
        start_index += len("Synonyms:")
        end_index = text.find("Antonyms:", start_index)
        if end_index == -1:
            end_index = len(text)
        
        synonyms_text = text[start_index:end_index].strip()
        return synonyms_text if synonyms_text else "No synonyms found."
    
    def extract_antonyms(self, text):
        """Extract antonyms from the text based on the 'Antonyms:' keyword."""
        start_index = text.find("Antonyms:")
        if start_index == -1:
            return "No antonyms found."
        
        start_index += len("Antonyms:")
        end_index = text.find("\n", start_index)
        if end_index == -1:
            end_index = len(text)
        
        synonyms_text = text[start_index:end_index].strip()
        return synonyms_text if synonyms_text else "No antonyms found."

    def _extract_text(self, soup, class_name, default_text):
        """Extract text from a BeautifulSoup object by class name."""
        try:
            return soup.find(class_=class_name).text
        except AttributeError:
            return default_text

    def add_word(self, word):
        """Add a new word to the dictionary."""
        if not word:
            self._show_message("Error", "Please enter a word to add.")
            return
        try:
            self.save_word_to_dictionary(word)
            self._show_message("Success", f"Word '{word}' added to the dictionary.")
            self.load_saved_words()
        except Exception as e:
            self._show_message("Error", f"An error occurred: {str(e)}")
            self.log_error(e)

    def save_word_to_dictionary(self, word):
        """Save a word to the dictionary file."""
        with open(self.dictionary_file, 'a') as file:
            file.write(word + "\n")
        print(f"Word '{word}' saved to dictionary.")

    def load_saved_words(self):
        """Load and display saved words."""
        self.display_words_frame.clear_words()
        if os.path.exists(self.dictionary_file):
            with open(self.dictionary_file, 'r') as file:
                words = file.readlines()
                for word in words:
                    self.display_words_frame.add_word(word.strip())

    def log_error(self, error):
        """Log an error to the error log file."""
        with open(self.error_log_file, "a") as file:
            file.write(f"{str(error)}\n")

    def _show_message(self, title, message):
        """Show a message box."""
        messagebox.showinfo(title, message)


class SearchFrame(tk.Frame):
    def __init__(self, master, search_callback):
        super().__init__(master)
        self.search_callback = search_callback
        self.create_widgets()

    def create_widgets(self):
        """Create search input and button."""
        self.search_label = tk.Label(self, text="Enter a word:")
        self.search_label.grid(row=0, column=0, padx=5)

        self.search_entry = tk.Entry(self)
        self.search_entry.grid(row=0, column=1, padx=5)

        self.search_button = tk.Button(self, text="Search", command=self.on_search)
        self.search_button.grid(row=0, column=2, padx=5)

    def on_search(self):
        """Handle search button click."""
        word = self.search_entry.get().strip()
        self.search_callback(word)


class ResultFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        """Create widgets to display word data."""
        self.meaning_label = tk.Label(self, text="Meaning:")
        self.meaning_label.grid(row=0, column=0, sticky="w")

        self.meaning_text = tk.Text(self, height=5, width=50, wrap="word")
        self.meaning_text.grid(row=1, column=0, pady=5)

        self.usage_label = tk.Label(self, text="Usage in Sentences:")
        self.usage_label.grid(row=2, column=0, sticky="w")

        self.usage_text = tk.Text(self, height=5, width=50, wrap="word")
        self.usage_text.grid(row=3, column=0, pady=5)

        self.synonyms_label = tk.Label(self, text="Synonyms:")
        self.synonyms_label.grid(row=4, column=0, sticky="w")

        self.synonyms_text = tk.Text(self, height=5, width=50, wrap="word")
        self.synonyms_text.grid(row=5, column=0, pady=5)

        self.antonyms_label = tk.Label(self, text="Antonyms:")
        self.antonyms_label.grid(row=6, column=0, sticky="w")

        self.antonyms_text = tk.Text(self, height=5, width=50, wrap="word")
        self.antonyms_text.grid(row=7, column=0, pady=5)

    def display_word_data(self, meaning, usage, synonyms, antonyms):
        """Update text widgets with word data."""
        self._update_text_widget(self.meaning_text, meaning)
        self._update_text_widget(self.usage_text, usage)
        self._update_text_widget(self.synonyms_text, synonyms)
        self._update_text_widget(self.antonyms_text, antonyms)

    def _update_text_widget(self, widget, text):
        """Update a text widget with new content."""
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)


class AddWordFrame(tk.Frame):
    def __init__(self, master, add_callback):
        super().__init__(master)
        self.add_callback = add_callback
        self.create_widgets()

    def create_widgets(self):
        """Create input and button to add new words."""
        self.add_word_label = tk.Label(self, text="Enter a word to add:")
        self.add_word_label.grid(row=0, column=0, padx=5)

        self.add_word_entry = tk.Entry(self)
        self.add_word_entry.grid(row=0, column=1, padx=5)
        
        self.add_button = tk.Button(self, text="Add Word", command=self.on_add)
        self.add_button.grid(row=0, column=2, padx=5)

    def on_add(self):
        """Handle add button click."""
        word = self.add_word_entry.get().strip()
        self.add_callback(word)


class DisplayWordsFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        """Create widget to display saved words."""
        self.display_words_label = tk.Label(self, text="Previously Added Words:")
        self.display_words_label.grid(row=0, column=0, sticky="w")

        self.display_words_listbox = tk.Listbox(self, width=50, height=10)
        self.display_words_listbox.grid(row=1, column=0, pady=5)

    def add_word(self, word):
        """Add a word to the listbox."""
        self.display_words_listbox.insert(tk.END, word)

    def clear_words(self):
        """Clear all words from the listbox."""
        self.display_words_listbox.delete(0, tk.END)


class HistoryFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        """Create widget to display word search history."""
        self.history_label = tk.Label(self, text="Search History:")
        self.history_label.grid(row=0, column=0, sticky="w")

        self.history_listbox = tk.Listbox(self, width=50, height=10)
        self.history_listbox.grid(row=1, column=0, pady=5)

    def add_to_history(self, word):
        """Add a word to the search history listbox."""
        self.history_listbox.insert(tk.END, word)


def main():
    root = tk.Tk()
    app = DictionaryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
