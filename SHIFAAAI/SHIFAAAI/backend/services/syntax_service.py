# syntax_service.py - Service d'analyse syntaxique pour SHIFAAAI

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
from datetime import datetime
import unicodedata

# =========================================================
# CLASSES DE DONNÉES
# =========================================================

@dataclass
class SyntaxToken:
    """Token avec informations syntaxiques"""
    text: str
    original: str
    pos: str  # Part of speech (NOUN, VERB, ADJ, etc.)
    lemma: str
    dependency: str  # Relation de dépendance (nsubj, dobj, amod, etc.)
    head: int  # Index du token parent
    children: List[int]  # Indices des tokens enfants
    start_char: int
    end_char: int
    position: int = -1  # Ajout de l'index du token

@dataclass
class Phrase:
    """Structure de phrase"""
    type: str  # NP, VP, PP, ADJP, etc.
    tokens: List[int]  # Indices des tokens
    text: str
    head: Optional[int] = None

@dataclass
class Clause:
    """Structure de proposition"""
    type: str  # main, subordinate, relative
    tokens: List[int]
    verb: Optional[int]  # Index du verbe principal
    subject: Optional[int]  # Index du sujet
    object: Optional[int]  # Index de l'objet
    text: str

@dataclass
class DependencyGraph:
    """Graphe de dépendances"""
    tokens: List[SyntaxToken]
    root: Optional[int]  # Index de la racine
    edges: List[Tuple[int, int, str]]  # (source, target, relation)
    depth: Dict[int, int]  # Profondeur de chaque token

@dataclass
class SyntaxAnalysis:
    """Résultat complet de l'analyse syntaxique"""
    original_text: str
    sentences: List[str]
    tokens: List[SyntaxToken]
    phrases: List[Phrase]
    clauses: List[Clause]
    dependency_graph: DependencyGraph
    statistics: Dict[str, Any]
    processing_time_ms: float

# =========================================================
# SERVICE D'ANALYSE SYNTAXIQUE
# =========================================================

class SyntaxService:
    """Service d'analyse syntaxique pour texte médical"""
    
    def __init__(self):
        self._init_pos_tags()
        self._init_dependency_rules()
        self._init_phrase_patterns()
    
    def _init_pos_tags(self):
        """Initialiser les tags POS et règles de détection"""
        
        # Dictionnaire des mots par catégorie grammaticale
        self.pos_dict = {
            # Noms (médicaux et généraux)
            'NOUN': {
                'medical': ['fièvre', 'toux', 'douleur', 'fatigue', 'gorge', 'nausée', 
                           'vomissement', 'diarrhée', 'essoufflement', 'vertige'],
                'general': ['patient', 'symptôme', 'maladie', 'traitement', 'médecin']
            },
            # Verbes
            'VERB': {
                'action': ['avoir', 'présenter', 'ressentir', 'souffrir', 'constater'],
                'etre': ['être', 'devenir', 'rester', 'sembler'],
                'auxiliary': ['avoir', 'être']
            },
            # Adjectifs
            'ADJ': {
                'intensity': ['fort', 'intense', 'léger', 'modéré', 'sévère', 'aigu', 'chronique'],
                'quality': ['rouge', 'gonflé', 'douloureux', 'fatigant']
            },
            # Adverbes
            'ADV': {
                'degree': ['très', 'beaucoup', 'peu', 'assez', 'extrêmement', 'trop'],
                'time': ["aujourd'hui", 'hier', 'maintenant', 'bientôt', 'récemment'],
                'negation': ['pas', 'ne', 'non', 'jamais', 'plus']
            },
            # Prépositions
            'ADP': ['dans', 'sur', 'sous', 'avec', 'sans', 'pour', 'par', 'chez', 'depuis', 'pendant'],
            # Conjonctions
            'CONJ': ['et', 'ou', 'mais', 'donc', 'car', 'ni'],
            # Déterminants
            'DET': ['le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'ce', 'cette', 'ces'],
            # Pronoms
            'PRON': ['je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'se', 'lui', 'leur'],
            # Nombres
            'NUM': re.compile(r'\b\d+(?:[.,]\d+)?\b'),
            # Ponctuation
            'PUNCT': ['.', ',', ';', ':', '!', '?', '(', ')', '[', ']', '{', '}']
        }
        
        # Patterns pour détection POS par regex
        self.pos_patterns = [
            (re.compile(r'\b\w+ant\b'), 'VERB'),  # Participe présent
            (re.compile(r'\b\w+é\b'), 'VERB'),    # Participe passé
            (re.compile(r'\b\w+ion\b'), 'NOUN'),  # Nom en -ion
            (re.compile(r'\b\w+eur\b'), 'NOUN'),  # Nom en -eur
            (re.compile(r'\b\w+if\b'), 'ADJ'),    # Adjectif en -if
            (re.compile(r'\b\w+ique\b'), 'ADJ'),  # Adjectif en -ique
        ]
    
    def _init_dependency_rules(self):
        """Initialiser les règles de dépendances"""
        
        # Règles pour la détection des relations de dépendance
        self.dependency_rules = {
            'nsubj': {  # Sujet nominal
                'head_pos': ['VERB', 'ADJ'],
                'dep_pos': ['NOUN', 'PRON'],
                'direction': 'left'
            },
            'dobj': {  # Objet direct
                'head_pos': ['VERB'],
                'dep_pos': ['NOUN'],
                'direction': 'right'
            },
            'amod': {  # Modificateur adjectival
                'head_pos': ['NOUN'],
                'dep_pos': ['ADJ'],
                'direction': 'left'
            },
            'advmod': {  # Modificateur adverbial
                'head_pos': ['VERB', 'ADJ'],
                'dep_pos': ['ADV'],
                'direction': 'left'
            },
            'nmod': {  # Modificateur nominal
                'head_pos': ['NOUN', 'VERB'],
                'dep_pos': ['NOUN'],
                'direction': 'right'
            },
            'det': {  # Déterminant
                'head_pos': ['NOUN'],
                'dep_pos': ['DET'],
                'direction': 'left'
            },
            'aux': {  # Auxiliaire
                'head_pos': ['VERB'],
                'dep_pos': ['VERB'],
                'direction': 'left',
                'aux_types': ['être', 'avoir']
            },
            'neg': {  # Négation
                'head_pos': ['VERB', 'ADJ'],
                'dep_pos': ['ADV'],
                'direction': 'left',
                'neg_words': ['pas', 'ne', 'non', 'jamais']
            },
            'prep': {  # Préposition
                'head_pos': ['VERB', 'NOUN', 'ADJ'],
                'dep_pos': ['ADP'],
                'direction': 'right'
            },
            'pobj': {  # Objet de préposition
                'head_pos': ['ADP'],
                'dep_pos': ['NOUN', 'PRON'],
                'direction': 'right'
            },
            'conj': {  # Conjonction
                'head_pos': ['NOUN', 'VERB', 'ADJ'],
                'dep_pos': ['NOUN', 'VERB', 'ADJ', 'CONJ'],
                'direction': 'right'
            }
        }
    
    def _init_phrase_patterns(self):
        """Initialiser les patterns pour la détection de phrases"""
        
        self.phrase_patterns = {
            'NP': [  # Nominal phrase
                (r'(?:DET\s+)?(?:ADJ\s+)*(?:NOUN\s*)+', 'DET? ADJ* NOUN+'),
                (r'(?:PRON\s+)?(?:NOUN\s*)+', 'PRON? NOUN+')
            ],
            'VP': [  # Verb phrase
                (r'(?:ADV\s+)*(?:VERB\s+)+(?:ADV\s+)*(?:NOUN\s*)*', 'ADV* VERB+ ADV* NOUN*'),
                (r'(?:AUX\s+)?(?:VERB\s+)+', 'AUX? VERB+')
            ],
            'PP': [  # Prepositional phrase
                (r'ADP\s+(?:DET\s+)?(?:ADJ\s+)*(?:NOUN\s*)+', 'ADP DET? ADJ* NOUN+')
            ],
            'ADJP': [  # Adjective phrase
                (r'(?:ADV\s+)*(?:ADJ\s*)+', 'ADV* ADJ+')
            ]
        }
    
    # =========================================================
    # MÉTHODES PRINCIPALES
    # =========================================================
    
    def analyze(self, text: str) -> SyntaxAnalysis:
        """
        Analyser la syntaxe du texte médical
        
        Args:
            text: Texte à analyser
            
        Returns:
            SyntaxAnalysis contenant tous les résultats
        """
        import time
        start_time = time.time()
        
        original_text = text
        
        # Prétraitement
        text_clean = self._preprocess(text)
        
        # Division en phrases
        sentences = self._split_sentences(text_clean)
        
        all_tokens = []
        all_phrases = []
        all_clauses = []
        
        for sent in sentences:
            # Tokenisation
            tokens = self._tokenize(sent)
            
            # POS tagging
            tokens = self._tag_pos(tokens)
            
            # Lemmatisation
            tokens = self._lemmatize_tokens(tokens)
            
            # Analyse des dépendances
            dep_graph = self._build_dependency_graph(tokens)
            
            # Extraction des phrases
            phrases = self._extract_phrases(tokens)
            
            # Extraction des propositions
            clauses = self._extract_clauses(tokens, dep_graph)
            
            # Ajuster les indices pour fusion
            offset = len(all_tokens)
            for p in phrases:
                p.tokens = [t + offset for t in p.tokens]
            for c in clauses:
                c.tokens = [t + offset for t in c.tokens]
            
            all_tokens.extend(tokens)
            all_phrases.extend(phrases)
            all_clauses.extend(clauses)
        
        # Graphe de dépendances global
        global_dep_graph = self._build_global_dependency_graph(all_tokens)
        
        # Statistiques
        statistics = self._calculate_statistics(all_tokens, all_phrases, all_clauses)
        
        processing_time = (time.time() - start_time) * 1000
        
        return SyntaxAnalysis(
            original_text=original_text,
            sentences=sentences,
            tokens=all_tokens,
            phrases=all_phrases,
            clauses=all_clauses,
            dependency_graph=global_dep_graph,
            statistics=statistics,
            processing_time_ms=round(processing_time, 2)
        )
    
    def _preprocess(self, text: str) -> str:
        """Prétraiter le texte"""
        text = unicodedata.normalize('NFKC', text)
        text = text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Diviser le texte en phrases"""
        # Patterns de fin de phrase
        sentence_delimiters = re.compile(r'[.!?]+(?:\s+|$)')
        
        sentences = []
        start = 0
        
        for match in sentence_delimiters.finditer(text):
            end = match.end()
            sentence = text[start:end].strip()
            if sentence:
                sentences.append(sentence)
            start = end
        
        # Dernière phrase sans ponctuation
        if start < len(text):
            remaining = text[start:].strip()
            if remaining:
                sentences.append(remaining)
        
        return sentences
    
    def _tokenize(self, text: str) -> List[SyntaxToken]:
        """Tokeniser le texte"""
        tokens = []
        # Tokenisation simple par mots
        words = text.split()
        current_pos = 0
        
        for idx, word in enumerate(words):
            # Trouver la position réelle dans le texte
            start = text.find(word, current_pos)
            if start == -1:
                start = current_pos
            end = start + len(word)
            current_pos = end
            
            token = SyntaxToken(
                text=word,
                original=word,
                pos='UNKNOWN',
                lemma=word,
                dependency='',
                head=-1,
                children=[],
                start_char=start,
                end_char=end,
                position=idx
            )
            tokens.append(token)
        
        return tokens
    
    def _tag_pos(self, tokens: List[SyntaxToken]) -> List[SyntaxToken]:
        """Taguer les parties du discours"""
        for token in tokens:
            word = token.text.lower()
            
            # Vérifier dans les dictionnaires
            pos_found = None
            
            for pos, data in self.pos_dict.items():
                if pos == 'NUM':
                    if data.match(word):
                        pos_found = pos
                        break
                elif isinstance(data, dict):
                    # Vérifier dans les sous-catégories
                    for subcat, words in data.items():
                        if word in words:
                            pos_found = pos
                            break
                    if pos_found:
                        break
                elif isinstance(data, list) and word in data:
                    pos_found = pos
                    break
            
            # Vérifier les patterns
            if not pos_found:
                for pattern, pos in self.pos_patterns:
                    if pattern.match(word):
                        pos_found = pos
                        break
            
            # Par défaut
            if not pos_found:
                # Heuristique simple
                if word.endswith('er') or word.endswith('ir') or word.endswith('re'):
                    pos_found = 'VERB'
                elif word.endswith('ment'):
                    pos_found = 'ADV'
                else:
                    pos_found = 'NOUN'
            
            token.pos = pos_found
        
        return tokens
    
    def _lemmatize_tokens(self, tokens: List[SyntaxToken]) -> List[SyntaxToken]:
        """Lemmatisation simple"""
        for token in tokens:
            word = token.text.lower()
            # Règles de lemmatisation
            if word.endswith('ent'):
                token.lemma = word[:-3] + 'er'
            elif word.endswith('ant'):
                token.lemma = word[:-3] + 'er'
            elif word.endswith('euse'):
                token.lemma = word[:-4] + 'eur'
            elif word.endswith('te'):
                token.lemma = word[:-2] + 't'
            elif word.endswith('s') and not word.endswith('ss'):
                token.lemma = word[:-1]
            else:
                token.lemma = word
        
        return tokens
    
    def _build_dependency_graph(self, tokens: List[SyntaxToken]) -> DependencyGraph:
        """Construire le graphe de dépendances"""
        # Identifier la racine (verbe principal ou premier nom)
        root_idx = -1
        for i, token in enumerate(tokens):
            if token.pos == 'VERB':
                root_idx = i
                break
        if root_idx == -1:
            for i, token in enumerate(tokens):
                if token.pos == 'NOUN':
                    root_idx = i
                    break
        if root_idx == -1 and tokens:
            root_idx = 0
        
        # Établir les dépendances
        edges = []
        for head_idx in range(len(tokens)):
            for dep_idx in range(len(tokens)):
                if head_idx != dep_idx:
                    # Règle simple: les modificateurs sont à gauche
                    if dep_idx < head_idx:
                        relation = self._determine_relation(tokens[head_idx], tokens[dep_idx], 'left')
                        if relation:
                            edges.append((head_idx, dep_idx, relation))
        
        # Calculer la profondeur
        depth = {root_idx: 0}
        queue = [root_idx]
        while queue:
            current = queue.pop(0)
            for edge in edges:
                if edge[0] == current:
                    child = edge[1]
                    depth[child] = depth[current] + 1
                    queue.append(child)
        
        # Mettre à jour les tokens
        for token in tokens:
            for edge in edges:
                if edge[1] == token.position:
                    token.dependency = edge[2]
                    token.head = edge[0]
                    break
        
        return DependencyGraph(
            tokens=tokens,
            root=root_idx,
            edges=edges,
            depth=depth
        )
    
    def _build_global_dependency_graph(self, tokens: List[SyntaxToken]) -> DependencyGraph:
        """Construire le graphe de dépendances global"""
        # Version simplifiée pour l'ensemble des tokens
        return DependencyGraph(
            tokens=tokens,
            root=0 if tokens else -1,
            edges=[],
            depth={}
        )
    
    def _determine_relation(self, head: SyntaxToken, dep: SyntaxToken, direction: str) -> Optional[str]:
        """Déterminer la relation de dépendance"""
        # Sujet nominal
        if head.pos == 'VERB' and dep.pos == 'NOUN' and direction == 'left':
            return 'nsubj'
        # Objet direct
        if head.pos == 'VERB' and dep.pos == 'NOUN' and direction == 'right':
            return 'dobj'
        # Modificateur adjectival
        if head.pos == 'NOUN' and dep.pos == 'ADJ' and direction == 'left':
            return 'amod'
        # Modificateur adverbial
        if head.pos == 'VERB' and dep.pos == 'ADV' and direction == 'left':
            return 'advmod'
        # Déterminant
        if head.pos == 'NOUN' and dep.pos == 'DET' and direction == 'left':
            return 'det'
        # Négation
        if dep.text in self.pos_dict['ADV']['negation']:
            return 'neg'
        return None
    
    def _extract_phrases(self, tokens: List[SyntaxToken]) -> List[Phrase]:
        """Extraire les groupes de mots (phrases)"""
        phrases = []
        current_phrase = []
        current_type = None
        
        for i, token in enumerate(tokens):
            if token.pos in ['NOUN', 'PRON']:
                if current_type != 'NP':
                    if current_phrase:
                        phrases.append(self._create_phrase(current_type, current_phrase, tokens))
                    current_phrase = [i]
                    current_type = 'NP'
                else:
                    current_phrase.append(i)
            elif token.pos == 'VERB':
                if current_type != 'VP':
                    if current_phrase:
                        phrases.append(self._create_phrase(current_type, current_phrase, tokens))
                    current_phrase = [i]
                    current_type = 'VP'
                else:
                    current_phrase.append(i)
            elif token.pos == 'ADP':
                if current_phrase:
                    phrases.append(self._create_phrase(current_type, current_phrase, tokens))
                current_phrase = [i]
                current_type = 'PP'
            else:
                if current_phrase:
                    phrases.append(self._create_phrase(current_type, current_phrase, tokens))
                    current_phrase = []
                    current_type = None
        
        if current_phrase:
            phrases.append(self._create_phrase(current_type, current_phrase, tokens))
        
        return phrases
    
    def _create_phrase(self, phrase_type: str, token_indices: List[int], 
                       tokens: List[SyntaxToken]) -> Phrase:
        """Créer un objet Phrase"""
        phrase_text = ' '.join([tokens[i].text for i in token_indices])
        return Phrase(
            type=phrase_type or '?',
            tokens=token_indices,
            text=phrase_text,
            head=token_indices[0] if token_indices else None
        )
    
    def _extract_clauses(self, tokens: List[SyntaxToken], 
                         dep_graph: DependencyGraph) -> List[Clause]:
        """Extraire les propositions"""
        clauses = []
        
        # Identifier les verbes
        verb_indices = [i for i, t in enumerate(tokens) if t.pos == 'VERB']
        
        for verb_idx in verb_indices:
            # Chercher le sujet
            subject = None
            obj = None
            
            for edge in dep_graph.edges:
                if edge[1] == verb_idx and edge[2] == 'nsubj':
                    subject = edge[0]
                if edge[0] == verb_idx and edge[2] == 'dobj':
                    obj = edge[1]
            
            # Collecter les tokens de la clause
            clause_tokens = self._get_clause_tokens(verb_idx, dep_graph)
            
            clause = Clause(
                type='main',
                tokens=clause_tokens,
                verb=verb_idx,
                subject=subject,
                object=obj,
                text=' '.join([tokens[i].text for i in sorted(clause_tokens)])
            )
            clauses.append(clause)
        
        return clauses
    
    def _get_clause_tokens(self, root_idx: int, dep_graph: DependencyGraph) -> List[int]:
        """Récupérer tous les tokens d'une clause"""
        tokens_set = {root_idx}
        queue = [root_idx]
        
        while queue:
            current = queue.pop(0)
            for edge in dep_graph.edges:
                if edge[0] == current:
                    if edge[1] not in tokens_set:
                        tokens_set.add(edge[1])
                        queue.append(edge[1])
                if edge[1] == current:
                    if edge[0] not in tokens_set:
                        tokens_set.add(edge[0])
                        queue.append(edge[0])
        
        return sorted(tokens_set)
    
    def _calculate_statistics(self, tokens: List[SyntaxToken], 
                              phrases: List[Phrase], 
                              clauses: List[Clause]) -> Dict[str, Any]:
        """Calculer les statistiques syntaxiques"""
        
        # Distribution des POS
        pos_dist = defaultdict(int)
        for token in tokens:
            pos_dist[token.pos] += 1
        
        # Longueur moyenne des phrases
        avg_phrase_len = sum(len(p.tokens) for p in phrases) / max(len(phrases), 1)
        
        # Complexité syntaxique
        complexity = 'faible'
        if len(clauses) > 3 or avg_phrase_len > 10:
            complexity = 'élevée'
        elif len(clauses) > 1 or avg_phrase_len > 5:
            complexity = 'moyenne'
        
        return {
            "total_tokens": len(tokens),
            "total_phrases": len(phrases),
            "total_clauses": len(clauses),
            "pos_distribution": dict(pos_dist),
            "avg_phrase_length": round(avg_phrase_len, 2),
            "syntactic_complexity": complexity,
            "verb_count": pos_dist.get('VERB', 0),
            "noun_count": pos_dist.get('NOUN', 0),
            "adj_count": pos_dist.get('ADJ', 0),
            "adv_count": pos_dist.get('ADV', 0)
        }
    
    # =========================================================
    # MÉTHODES SPÉCIALISÉES
    # =========================================================
    
    def extract_verb_phrases(self, text: str) -> List[str]:
        """Extraire les phrases verbales"""
        result = self.analyze(text)
        return [p.text for p in result.phrases if p.type == 'VP']
    
    def extract_noun_phrases(self, text: str) -> List[str]:
        """Extraire les phrases nominales"""
        result = self.analyze(text)
        return [p.text for p in result.phrases if p.type == 'NP']
    
    def get_dependency_summary(self, text: str) -> Dict[str, int]:
        """Obtenir un résumé des dépendances"""
        result = self.analyze(text)
        dep_counts = defaultdict(int)
        for edge in result.dependency_graph.edges:
            dep_counts[edge[2]] += 1
        return dict(dep_counts)
    
    def get_sentence_structure(self, text: str) -> List[Dict[str, Any]]:
        """Obtenir la structure des phrases"""
        result = self.analyze(text)
        structures = []
        
        for i, clause in enumerate(result.clauses[:5]):
            structures.append({
                "sentence_index": i,
                "type": clause.type,
                "verb": result.tokens[clause.verb].text if clause.verb is not None else None,
                "subject": result.tokens[clause.subject].text if clause.subject is not None else None,
                "object": result.tokens[clause.object].text if clause.object is not None else None,
                "text": clause.text
            })
        
        return structures

# =========================================================
# SERVICE SINGLETON
# =========================================================

_syntax_service_instance = None

def get_syntax_service() -> SyntaxService:
    """Obtenir l'instance unique du service syntaxique"""
    global _syntax_service_instance
    if _syntax_service_instance is None:
        _syntax_service_instance = SyntaxService()
    return _syntax_service_instance

# =========================================================
# ROUTES FLASK
# =========================================================

def create_syntax_routes():
    """Créer les routes Flask pour le service syntaxique"""
    from flask import Blueprint, request, jsonify
    
    syntax_bp = Blueprint('syntax', __name__, url_prefix='/api/syntax')
    service = get_syntax_service()
    
    @syntax_bp.route('/analyze', methods=['POST'])
    def analyze():
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        result = service.analyze(text)
        return jsonify({
            "success": True,
            "result": asdict(result)
        })
    
    @syntax_bp.route('/phrases', methods=['POST'])
    def get_phrases():
        data = request.get_json()
        text = data.get('text', '')
        
        result = service.analyze(text)
        return jsonify({
            "success": True,
            "noun_phrases": [p.text for p in result.phrases if p.type == 'NP'],
            "verb_phrases": [p.text for p in result.phrases if p.type == 'VP']
        })
    
    @syntax_bp.route('/dependencies', methods=['POST'])
    def get_dependencies():
        data = request.get_json()
        text = data.get('text', '')
        
        deps = service.get_dependency_summary(text)
        return jsonify({
            "success": True,
            "dependencies": deps
        })
    
    return syntax_bp

# =========================================================
# TESTS
# =========================================================

def test_syntax_service():
    """Tester le service syntaxique"""
    service = get_syntax_service()
    
    print("\n" + "="*60)
    print("📐 TEST DU SERVICE SYNTAXIQUE")
    print("="*60)
    
    test_texts = [
        "J'ai une forte fièvre et une toux sèche",
        "Le patient présente une douleur thoracique intense",
        "Je n'ai pas de fièvre mais j'ai des nausées",
        "La migraine avec nausée et sensibilité à la lumière dure depuis 3 jours"
    ]
    
    for text in test_texts:
        print(f"\n📝 Texte: {text}")
        print("-"*40)
        
        result = service.analyze(text)
        
        print(f"   Phrases: {len(result.sentences)}")
        print(f"   Tokens: {result.statistics['total_tokens']}")
        print(f"   POS: NOUN={result.statistics['noun_count']}, VERB={result.statistics['verb_count']}")
        print(f"   Phrases nominales: {len([p for p in result.phrases if p.type == 'NP'])}")
        print(f"   Propositions: {result.statistics['total_clauses']}")
        print(f"   Complexité: {result.statistics['syntactic_complexity']}")
        print(f"   Temps: {result.processing_time_ms}ms")
        
        # Afficher les phrases nominales
        noun_phrases = [p.text for p in result.phrases if p.type == 'NP'][:3]
        if noun_phrases:
            print(f"   NP: {', '.join(noun_phrases)}")

if __name__ == "__main__":
    test_syntax_service()
    
    # Démarrer le serveur Flask
    try:
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(create_syntax_routes())
        
        print("\n" + "="*60)
        print("🚀 SERVEUR SYNTAXIQUE DÉMARRÉ")
        print("="*60)
        print("📍 Endpoints:")
        print("   POST /api/syntax/analyze      - Analyse syntaxique complète")
        print("   POST /api/syntax/phrases      - Extraction des phrases")
        print("   POST /api/syntax/dependencies - Analyse des dépendances")
        print("="*60)
        
        app.run(host="127.0.0.1", port=5004, debug=True)
    except ImportError:
        print("Flask non installé - impossible de démarrer le serveur")