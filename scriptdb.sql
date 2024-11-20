
/*
Auteur : Nathan Lauziere
desc: script de creation de base de donne de gestion de commande de pizza
derniere modification : 11/20/24
*/
CREATE DATABASE Pizzeria;

use Pizzeria;

CREATE TABLE Pizza (
id INT primary Key AUTO_INCREMENT,
croute enum('Classique', 'Mince', 'Épaisse'),
sauces enum('Tomate', 'Spaghetti', 'Alfredo'),
garniture1 enum('rien','Pepperoni', 'Champignons', 'Oignons', 'Poivrons', 'Olives', 'Anchois', 'Bacon', 'Poulet', 'Maïs', 'Fromage', 'Piments forts'),
garniture2 enum('rien','Pepperoni', 'Champignons', 'Oignons', 'Poivrons', 'Olives', 'Anchois', 'Bacon', 'Poulet', 'Maïs', 'Fromage', 'Piments forts'),
garniture3 enum('rien','Pepperoni', 'Champignons', 'Oignons', 'Poivrons', 'Olives', 'Anchois', 'Bacon', 'Poulet', 'Maïs', 'Fromage', 'Piments forts'),
garniture4 enum('rien','Pepperoni', 'Champignons', 'Oignons', 'Poivrons', 'Olives', 'Anchois', 'Bacon', 'Poulet', 'Maïs', 'Fromage', 'Piments forts')
);
CREATE TABLE Client (
id INT PRIMARY KEY AUTO_INCREMENT,
nom VARCHAR(255) NOT NULL,
tel bigint(10) UNSIGNED NOT NULL,
mdp VARCHAR(255) NOT NULL,
addresse VARCHAR(255) NOT NULL
);

CREATE TABLE Commande (
id_commande INT primary key auto_increment,
id_client INT,
id_pizza INT,
foreign key (id_client) references Client(id),
foreign key (id_pizza) references Pizza(id));

create table liste_commande (
id_commande INT,
status enum('enPreparation','enLivraison','completer'),
foreign key (id_commande) references Commande(id_commande));


DELIMITER $$

CREATE TRIGGER after_commande_insert
AFTER INSERT ON Commande
FOR EACH ROW
BEGIN
INSERT INTO liste_commande (id_commande, status)
VALUES (NEW.id_commande, 'enPreparation');
END $$

DELIMITER ;