# test_library_system.py
import pytest
from library_system import (
    Author, Book, BookCopy, Reader, BioAlert, Library, CopyStatus
)


class TestAuthor:
    """Tests para la clase Author."""
    
    def test_author_creation(self):
        author = Author("Somerville", "1950-01-01")
        assert author.get_name() == "Somerville"
        assert author.get_birth_date() == "1950-01-01"


class TestBook:
    """Tests para la clase Book."""
    
    def test_book_creation(self):
        author = Author("Somerville", "1950-01-01")
        book = Book("Software Engineering", 2020, author)
        
        assert book.get_title() == "Software Engineering"
        assert book.get_year() == 2020
        assert book.get_author() == author
    
    def test_book_full_info(self):
        author = Author("Somerville", "1950-01-01")
        book = Book("Software Engineering", 2020, author)
        
        expected = "Software Engineering (2020) - Somerville"
        assert book.get_full_info() == expected


class TestBookCopy:
    """Tests para la clase BookCopy."""
    
    def test_copy_creation(self):
        author = Author("Somerville", "1950-01-01")
        book = Book("Software Engineering", 2020, author)
        copy = BookCopy("C001", book)
        
        assert copy.get_id() == "C001"
        assert copy.get_book() == book
        assert copy.is_available() is True
    
    def test_copy_status_change(self):
        author = Author("Somerville", "1950-01-01")
        book = Book("Software Engineering", 2020, author)
        copy = BookCopy("C001", book)
        
        copy.set_status(CopyStatus.BORROWED)
        assert copy.get_status() == CopyStatus.BORROWED
        assert copy.is_available() is False
    
    def test_copy_all_statuses(self):
        author = Author("Somerville", "1950-01-01")
        book = Book("Software Engineering", 2020, author)
        copy = BookCopy("C001", book)
        
        for status in CopyStatus:
            copy.set_status(status)
            assert copy.get_status() == status


class TestReader:
    """Tests para la clase Reader."""
    
    def test_reader_creation(self):
        reader = Reader("John Doe", "john@example.com")
        assert reader.get_name() == "John Doe"
        assert reader.get_email() == "john@example.com"
        assert reader.get_penalty_days() == 0
        assert len(reader.get_borrowed_books()) == 0
    
    def test_reader_can_borrow_initially(self):
        reader = Reader("John Doe", "john@example.com")
        assert reader.can_borrow() is True
    
    def test_reader_cannot_borrow_with_penalty(self):
        reader = Reader("John Doe", "john@example.com")
        reader.add_penalty(1)  # 1 día de retraso = 2 días de multa
        assert reader.get_penalty_days() == 2
        assert reader.can_borrow() is False
    
    def test_reader_borrow_book_success(self):
        reader = Reader("John Doe", "john@example.com")
        author = Author("Somerville", "1950-01-01")
        book = Book("Software Engineering", 2020, author)
        copy = BookCopy("C001", book)
        
        result = reader.borrow_book(copy)
        assert result is True
        assert len(reader.get_borrowed_books()) == 1
        assert copy.get_status() == CopyStatus.BORROWED
    
    def test_reader_max_three_books(self):
        reader = Reader("John Doe", "john@example.com")
        author = Author("Somerville", "1950-01-01")
        book = Book("Software Engineering", 2020, author)
        
        copy1 = BookCopy("C001", book)
        copy2 = BookCopy("C002", book)
        copy3 = BookCopy("C003", book)
        copy4 = BookCopy("C004", book)
        
        assert reader.borrow_book(copy1) is True
        assert reader.borrow_book(copy2) is True
        assert reader.borrow_book(copy3) is True
        assert reader.borrow_book(copy4) is False  # Excede el límite
        assert len(reader.get_borrowed_books()) == 3
    
    def test_reader_return_book(self):
        reader = Reader("John Doe", "john@example.com")
        author = Author("Somerville", "1950-01-01")
        book = Book("Software Engineering", 2020, author)
        copy = BookCopy("C001", book)
        
        reader.borrow_book(copy)
        assert len(reader.get_borrowed_books()) == 1
        
        reader.return_book(copy)
        assert len(reader.get_borrowed_books()) == 0
        assert copy.get_status() == CopyStatus.AVAILABLE
    
    def test_penalty_calculation(self):
        reader = Reader("John Doe", "john@example.com")
        reader.add_penalty(3)  # 3 días de retraso = 6 días de multa
        assert reader.get_penalty_days() == 6
    
    def test_reduce_penalty(self):
        reader = Reader("John Doe", "john@example.com")
        reader.add_penalty(5)  # 10 días de multa
        reader.reduce_penalty(3)
        assert reader.get_penalty_days() == 7
    
    def test_reduce_penalty_minimum_zero(self):
        reader = Reader("John Doe", "john@example.com")
        reader.add_penalty(2)  # 4 días de multa
        reader.reduce_penalty(10)  # Reducir más de lo que tiene
        assert reader.get_penalty_days() == 0


class TestBioAlert:
    """Tests para la clase BioAlert (Singleton)."""
    
    def test_bioalert_singleton(self):
        instance1 = BioAlert.get_instance()
        instance2 = BioAlert.get_instance()
        assert instance1 is instance2
    
    def test_subscribe_to_book(self):
        bio_alert = BioAlert.get_instance()
        bio_alert.subscribe("Software Engineering 10th", "student@example.com")
        
        assert bio_alert.is_subscribed("Software Engineering 10th", "student@example.com")
    
    def test_multiple_subscribers(self):
        bio_alert = BioAlert.get_instance()
        bio_alert.subscribe("Python Programming", "user1@example.com")
        bio_alert.subscribe("Python Programming", "user2@example.com")
        
        subscribers = bio_alert.get_subscribers("Python Programming")
        assert len(subscribers) >= 2
        assert "user1@example.com" in subscribers
        assert "user2@example.com" in subscribers
    
    def test_notify_availability(self, capsys):
        bio_alert = BioAlert.get_instance()
        bio_alert.subscribe("Test Book", "test@example.com")
        
        bio_alert.notify_availability("Test Book")
        captured = capsys.readouterr()
        assert "test@example.com" in captured.out
        assert "Test Book" in captured.out


class TestLibrary:
    """Tests para la clase Library."""
    
    @pytest.fixture
    def setup_library(self):
        """Fixture para configurar biblioteca básica."""
        library = Library()
        somerville = Author("Somerville", "1950-01-01")
        return library, somerville
    
    def test_add_book_and_copy(self, setup_library):
        library, somerville = setup_library
        book = Book("Software Engineering", 2020, somerville)
        copy = BookCopy("C001", book)
        
        library.add_book(book)
        library.add_copy(copy)
        
        assert len(library.books) == 1
        assert len(library.copies) == 1
    
    def test_register_reader(self, setup_library):
        library, _ = setup_library
        reader = Reader("John Doe", "john@example.com")
        library.register_reader(reader)
        
        assert len(library.readers) == 1
        assert library.readers[0] == reader
    
    def test_count_copies_by_author(self, setup_library):
        library, somerville = setup_library
        book1 = Book("Software Engineering", 2015, somerville)
        book2 = Book("Software Engineering", 2020, somerville)
        
        library.add_copy(BookCopy("C001", book1))
        library.add_copy(BookCopy("C002", book1))
        library.add_copy(BookCopy("C003", book2))
        
        assert library.count_copies_by_author("Somerville") == 3
    
    def test_count_copies_case_insensitive(self, setup_library):
        library, somerville = setup_library
        book = Book("Software Engineering", 2020, somerville)
        library.add_copy(BookCopy("C001", book))
        
        assert library.count_copies_by_author("somerville") == 1
        assert library.count_copies_by_author("SOMERVILLE") == 1
    
    def test_find_copies_by_author(self, setup_library):
        library, somerville = setup_library
        book = Book("Software Engineering", 2020, somerville)
        copy1 = BookCopy("C001", book)
        copy2 = BookCopy("C002", book)
        
        library.add_copy(copy1)
        library.add_copy(copy2)
        
        copies = library.find_copies_by_author("Somerville")
        assert len(copies) == 2
        assert copy1 in copies
        assert copy2 in copies
    
    def test_find_available_copy(self, setup_library):
        library, somerville = setup_library
        book = Book("Software Engineering", 2020, somerville)
        copy1 = BookCopy("C001", book)
        copy2 = BookCopy("C002", book)
        
        library.add_copy(copy1)
        library.add_copy(copy2)
        
        copy1.set_status(CopyStatus.BORROWED)
        
        available = library.find_available_copy("Software Engineering", 2020)
        assert available is not None
        assert available.get_id() == "C002"
    
    def test_find_available_copy_none_available(self, setup_library):
        library, somerville = setup_library
        book = Book("Software Engineering", 2020, somerville)
        copy = BookCopy("C001", book)
        copy.set_status(CopyStatus.BORROWED)
        
        library.add_copy(copy)
        
        available = library.find_available_copy("Software Engineering", 2020)
        assert available is None
    
    def test_borrow_book_success(self, setup_library):
        library, somerville = setup_library
        book = Book("Software Engineering", 2020, somerville)
        copy = BookCopy("C001", book)
        reader = Reader("John Doe", "john@example.com")
        
        library.add_copy(copy)
        library.register_reader(reader)
        
        result = library.borrow_book(reader, copy)
        assert result is True
        assert len(reader.get_borrowed_books()) == 1
    
    def test_borrow_book_with_penalty(self, setup_library):
        library, somerville = setup_library
        book = Book("Software Engineering", 2020, somerville)
        copy = BookCopy("C001", book)
        reader = Reader("John Doe", "john@example.com")
        reader.add_penalty(1)
        
        library.add_copy(copy)
        
        result = library.borrow_book(reader, copy)
        assert result is False
        assert len(reader.get_borrowed_books()) == 0
    
    def test_subscribe_to_book(self, setup_library):
        library, _ = setup_library
        library.subscribe_to_book("Software Engineering 10th", "student@example.com")
        
        assert library.bio_alert.is_subscribed("Software Engineering 10th", "student@example.com")
    
    def test_get_all_books_by_author(self, setup_library):
        library, somerville = setup_library
        book1 = Book("Software Engineering", 2015, somerville)
        book2 = Book("Software Engineering", 2020, somerville)
        book3 = Book("Requirements Engineering", 2018, somerville)
        
        library.add_copy(BookCopy("C001", book1))
        library.add_copy(BookCopy("C002", book1))  # Duplicado
        library.add_copy(BookCopy("C003", book2))
        library.add_copy(BookCopy("C004", book3))
        
        books = library.get_all_books_by_author("Somerville")
        assert len(books) == 3  # No duplicados
    
    def test_list_copies_details(self, setup_library):
        library, somerville = setup_library
        book = Book("Software Engineering", 2020, somerville)
        copy1 = BookCopy("C001", book)
        copy2 = BookCopy("C002", book)
        
        library.add_copy(copy1)
        library.add_copy(copy2)
        
        details = library.list_copies_details("Somerville")
        assert len(details) == 2
        assert "C001" in details[0]
        assert "C002" in details[1]


# Test de integración completo
class TestIntegration:
    """Test de integración del escenario del diálogo."""
    
    def test_dialogue_scenario(self):
        # Setup
        library = Library()
        somerville = Author("Somerville", "1945-03-20")
        student = Reader("Estudiante", "estudiante@uni.edu")
        library.register_reader(student)
        
        # Crear 15 copias de libros de Somerville
        book_8th = Book("Software Engineering", 2006, somerville)
        book_9th = Book("Software Engineering", 2010, somerville)
        book_9th_es = Book("Ingeniería de Software", 2010, somerville)
        book_10th = Book("Software Engineering", 2015, somerville)
        
        for i in range(5):
            library.add_copy(BookCopy(f"C00{i+1}", book_8th))
        for i in range(5):
            library.add_copy(BookCopy(f"C00{i+6}", book_9th))
        for i in range(4):
            library.add_copy(BookCopy(f"C0{i+11}", book_9th_es))
        library.add_copy(BookCopy("C015", book_10th))
        
        # Estudiante pregunta cuántos libros de Somerville hay
        count = library.count_copies_by_author("Somerville")
        assert count == 15
        
        # Buscar copia de Software Engineering 10th
        copy_10th = library.find_available_copy("Software Engineering", 2015)
        assert copy_10th is not None
        assert copy_10th.get_id() == "C015"
        
        # El libro no tiene copias adicionales (es el único)
        copies_10th = [c for c in library.copies 
                       if c.get_book().get_title() == "Software Engineering" 
                       and c.get_book().get_year() == 2015]
        assert len(copies_10th) == 1
        
        # Estudiante se suscribe al BioAlert
        library.subscribe_to_book("Software Engineering 10th Edition", 
                                  student.get_email())
        assert library.bio_alert.is_subscribed("Software Engineering 10th Edition",
                                               student.get_email())