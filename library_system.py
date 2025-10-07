# library_system.py
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime

class CopyStatus(Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"
    DELAYED = "delayed"
    IN_REPAIR = "in_repair"


class Author:
    
    def __init__(self, name: str, birth_date: str):
        self.name = name
        self.birth_date = birth_date
    
    def get_name(self) -> str:
        return self.name
    
    def get_birth_date(self) -> str:
        return self.birth_date


class Book:
    
    def __init__(self, title: str, year: int, author: Author):
        self.title = title
        self.year = year
        self.author = author
    
    def get_title(self) -> str:
        return self.title
    
    def get_year(self) -> int:
        return self.year
    
    def get_author(self) -> Author:
        return self.author
    
    def get_full_info(self) -> str:
        return f"{self.title} ({self.year}) - {self.author.get_name()}"


class BookCopy:
    
    def __init__(self, copy_id: str, book: Book):
        self.copy_id = copy_id
        self.book = book
        self.status = CopyStatus.AVAILABLE
    
    def get_id(self) -> str:
        return self.copy_id
    
    def get_book(self) -> Book:
        return self.book
    
    def get_status(self) -> CopyStatus:
        return self.status
    
    def set_status(self, status: CopyStatus) -> None:
        self.status = status
    
    def is_available(self) -> bool:
        return self.status == CopyStatus.AVAILABLE


class Reader:
    
    MAX_BORROWED_BOOKS = 3
    PENALTY_MULTIPLIER = 2  
    
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self.borrowed_books: List[BookCopy] = []
        self.penalty_days = 0
    
    def can_borrow(self) -> bool:
        """Verifica si el lector puede pedir prestado un libro."""
        return len(self.borrowed_books) < self.MAX_BORROWED_BOOKS and self.penalty_days == 0
    
    def borrow_book(self, copy: BookCopy) -> bool:
        """Intenta pedir prestado un libro."""
        if self.can_borrow() and copy.is_available():
            self.borrowed_books.append(copy)
            copy.set_status(CopyStatus.BORROWED)
            return True
        return False
    
    def return_book(self, copy: BookCopy) -> None:
        """Devuelve un libro prestado."""
        if copy in self.borrowed_books:
            self.borrowed_books.remove(copy)
            copy.set_status(CopyStatus.AVAILABLE)
    
    def add_penalty(self, delay_days: int) -> None:
        """Agrega días de multa (2 días de multa por cada día de retraso)."""
        self.penalty_days += delay_days * self.PENALTY_MULTIPLIER
    
    def reduce_penalty(self, days: int) -> None:
        """Reduce días de multa."""
        self.penalty_days = max(0, self.penalty_days - days)
    
    def get_name(self) -> str:
        return self.name
    
    def get_email(self) -> str:
        return self.email
    
    def get_borrowed_books(self) -> List[BookCopy]:
        return self.borrowed_books.copy()
    
    def get_penalty_days(self) -> int:
        return self.penalty_days


class BioAlert:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BioAlert, cls).__new__(cls)
            cls._instance.subscriptions: Dict[str, List[str]] = {}
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'BioAlert':
        if cls._instance is None:
            cls._instance = BioAlert()
        return cls._instance
    
    def subscribe(self, book_title: str, email: str) -> None:
        if book_title not in self.subscriptions:
            self.subscriptions[book_title] = []
        if email not in self.subscriptions[book_title]:
            self.subscriptions[book_title].append(email)
    
    def notify_availability(self, book_title: str) -> List[str]:
        emails = self.subscriptions.get(book_title, [])
        for email in emails:
            self._send_email(email, book_title)
        return emails
    
    def _send_email(self, email: str, book_title: str) -> None:
        print(f"Email sent to {email}: '{book_title}' is now available")
    
    def is_subscribed(self, book_title: str, email: str) -> bool:
        return email in self.subscriptions.get(book_title, [])
    
    def get_subscribers(self, book_title: str) -> List[str]:
        return self.subscriptions.get(book_title, []).copy()


class Library:
    
    MAX_LOAN_DAYS = 30
    
    def __init__(self):
        self.books: List[Book] = []
        self.copies: List[BookCopy] = []
        self.readers: List[Reader] = []
        self.bio_alert = BioAlert.get_instance()
    
    def add_book(self, book: Book) -> None:
        self.books.append(book)
    
    def add_copy(self, copy: BookCopy) -> None:
        self.copies.append(copy)
    
    def register_reader(self, reader: Reader) -> None:
        self.readers.append(reader)
    
    def count_copies_by_author(self, author_name: str) -> int:
        return sum(1 for copy in self.copies 
                   if copy.get_book().get_author().get_name().lower() == author_name.lower())
    
    def find_copies_by_author(self, author_name: str) -> List[BookCopy]:
        return [copy for copy in self.copies 
                if copy.get_book().get_author().get_name().lower() == author_name.lower()]
    
    def find_available_copy(self, title: str, year: int) -> Optional[BookCopy]:
        for copy in self.copies:
            book = copy.get_book()
            if (book.get_title().lower() == title.lower() and 
                book.get_year() == year and 
                copy.is_available()):
                return copy
        return None
    
    def borrow_book(self, reader: Reader, copy: BookCopy) -> bool:
        if reader.can_borrow() and copy.is_available():
            return reader.borrow_book(copy)
        return False
    
    def subscribe_to_book(self, book_title: str, email: str) -> None:
        self.bio_alert.subscribe(book_title, email)
    
    def get_all_books_by_author(self, author_name: str) -> List[Book]:
        seen = set()
        result = []
        for copy in self.copies:
            book = copy.get_book()
            if book.get_author().get_name().lower() == author_name.lower():
                key = (book.get_title(), book.get_year())
                if key not in seen:
                    seen.add(key)
                    result.append(book)
        return result
    
    def list_copies_details(self, author_name: str) -> List[str]:
        copies = self.find_copies_by_author(author_name)
        return [f"{copy.get_book().get_full_info()} - Copy {copy.get_id()}" 
                for copy in copies]