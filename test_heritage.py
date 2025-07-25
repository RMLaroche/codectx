"""Test file demonstrating class heritage for unified format"""

from abc import ABC, abstractmethod
from typing import List, Optional

class Animal(ABC):
    """Base abstract animal class"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def make_sound(self) -> str:
        pass

class Mammal(Animal):
    """Mammal class inheriting from Animal"""
    
    def __init__(self, name: str, fur_color: str):
        super().__init__(name)
        self.fur_color = fur_color
    
    def give_birth(self) -> None:
        print(f"{self.name} gives birth to live young")

class Dog(Mammal):
    """Dog class with multiple inheritance features"""
    
    def __init__(self, name: str, breed: str):
        super().__init__(name, "brown")
        self.breed = breed
    
    def make_sound(self) -> str:
        return "Woof!"
    
    @staticmethod
    def bark_loudly() -> None:
        print("WOOF WOOF!")
    
    @property
    def description(self) -> str:
        return f"{self.name} is a {self.breed}"

def create_animal_factory(animal_type: str) -> Animal:
    """Factory function for creating animals"""
    if animal_type == "dog":
        return Dog("Buddy", "Golden Retriever")
    raise ValueError("Unknown animal type")