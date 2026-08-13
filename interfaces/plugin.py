from abc import ABC, abstractmethod

from interfaces.skill import Skill


class Plugin(ABC):
   

    @property
    @abstractmethod
    def plugin_id(self) -> str:
      
        pass

    @abstractmethod
    def initialize(self) -> None:
        
        pass

    @abstractmethod
    def shutdown(self) -> None:
      
        pass

    @abstractmethod
    def get_skills(self) -> list[Skill]:
     
        pass