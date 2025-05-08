import os
import logging
import json
import datetime
import time
import sqlite3
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class AdvancedMemorySystem:
    """
    Advanced Memory System for Synapse Chamber
    
    Implements sophisticated memory storage and retrieval mechanisms including:
    - Semantic search across stored conversations and threads
    - Long-term and short-term memory storage
    - Context-aware memory retrieval
    - Memory consolidation and knowledge extraction
    - Distributed storage with PostgreSQL for structured data and vector store for embeddings
    """
    
    def __init__(self, memory_system=None):
        self.logger = logging.getLogger(__name__)
        self.base_memory_system = memory_system
        self.memory_dir = "data/advanced_memory"
        
        # Database connection
        self.db_connection = None
        self.connection_pool = None
        self.is_connected = False
        
        # Memory indexes
        self.semantic_index = None
        self.conversation_vectorizer = None
        self.conversation_vectors = None
        self.conversation_ids = []
        
        # Memory cache
        self.memory_cache = {}
        self.cache_expiry = {}
        self.cache_max_age = 600  # 10 minutes
        
        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Initialize memory system
        self._init_memory_system()
    
    def _init_memory_system(self):
        """Initialize the memory system components"""
        # Initialize database connection
        self._init_database()
        
        # Initialize semantic index
        self._init_semantic_index()
        
        # Load any cached data
        self._load_cached_data()
    
    def _init_database(self):
        """Initialize database connection"""
        try:
            # Try to connect to PostgreSQL
            db_url = os.environ.get('DATABASE_URL')
            
            if db_url:
                # Create a connection pool
                self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=db_url
                )
                
                self.is_connected = True
                self.logger.info("Connected to PostgreSQL database")
                
                # Ensure memory tables exist
                self._ensure_memory_tables()
            else:
                self.logger.warning("No DATABASE_URL found, advanced memory features will be limited")
                self.is_connected = False
        except Exception as e:
            self.logger.error(f"Error connecting to database: {str(e)}")
            self.is_connected = False
    
    def _get_db_connection(self):
        """Get a connection from the pool"""
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None
    
    def _return_db_connection(self, conn):
        """Return a connection to the pool"""
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)
    
    def _ensure_memory_tables(self):
        """Ensure all required tables exist in the database"""
        if not self.is_connected:
            return
            
        conn = self._get_db_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                # Create memory_items table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_items (
                        id SERIAL PRIMARY KEY,
                        memory_type VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB,
                        source VARCHAR(100),
                        importance FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        embedding_id VARCHAR(100),
                        is_consolidated BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Create memory_contexts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_contexts (
                        id SERIAL PRIMARY KEY,
                        context_name VARCHAR(100) NOT NULL,
                        context_data JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create memory_links table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_links (
                        id SERIAL PRIMARY KEY,
                        source_id INTEGER REFERENCES memory_items(id) ON DELETE CASCADE,
                        target_id INTEGER REFERENCES memory_items(id) ON DELETE CASCADE,
                        link_type VARCHAR(50),
                        weight FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create vector_embeddings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vector_embeddings (
                        id VARCHAR(100) PRIMARY KEY,
                        embedding FLOAT[] NOT NULL,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create consolidated_knowledge table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS consolidated_knowledge (
                        id SERIAL PRIMARY KEY,
                        knowledge_area VARCHAR(100) NOT NULL,
                        content TEXT NOT NULL,
                        source_ids INTEGER[],
                        confidence FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_memory_items_type ON memory_items(memory_type);
                    CREATE INDEX IF NOT EXISTS idx_memory_items_importance ON memory_items(importance);
                    CREATE INDEX IF NOT EXISTS idx_memory_items_consolidated ON memory_items(is_consolidated);
                    CREATE INDEX IF NOT EXISTS idx_memory_contexts_name ON memory_contexts(context_name);
                """)
                
                conn.commit()
                self.logger.info("Memory tables initialized successfully")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error creating memory tables: {str(e)}")
        finally:
            self._return_db_connection(conn)
    
    def _init_semantic_index(self):
        """Initialize the semantic index for memory retrieval"""
        # Initialize TF-IDF vectorizer for conversation content
        self.conversation_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Load existing conversation data for indexing
        self._update_semantic_index()
    
    def _update_semantic_index(self):
        """Update the semantic index with the latest conversation data"""
        if not self.base_memory_system:
            self.logger.warning("Base memory system not available, semantic indexing disabled")
            return
            
        try:
            # Get all conversations from base memory system
            conversations = self.base_memory_system.get_conversations(limit=1000)
            
            if not conversations:
                self.logger.info("No conversations found for semantic indexing")
                return
                
            # Prepare text for vectorization
            texts = []
            self.conversation_ids = []
            
            for conv in conversations:
                # Combine all messages into a single text
                messages = [msg.get('content', '') for msg in conv.get('messages', [])]
                text = ' '.join(messages)
                
                if text.strip():
                    texts.append(text)
                    self.conversation_ids.append(conv.get('id'))
            
            if not texts:
                self.logger.info("No conversation content for semantic indexing")
                return
                
            # Create TF-IDF matrix
            self.conversation_vectors = self.conversation_vectorizer.fit_transform(texts)
            self.logger.info(f"Updated semantic index with {len(texts)} conversations")
        except Exception as e:
            self.logger.error(f"Error updating semantic index: {str(e)}")
    
    def _load_cached_data(self):
        """Load cached memory data"""
        cache_path = os.path.join(self.memory_dir, "memory_cache.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    self.memory_cache = cache_data.get('cache', {})
                    self.cache_expiry = cache_data.get('expiry', {})
                    
                    # Convert string keys to appropriate types
                    self.memory_cache = {key: value for key, value in self.memory_cache.items()}
                    self.cache_expiry = {key: value for key, value in self.cache_expiry.items()}
                    
                    # Filter out expired cache entries
                    now = time.time()
                    for key in list(self.cache_expiry.keys()):
                        if self.cache_expiry[key] < now:
                            self.memory_cache.pop(key, None)
                            self.cache_expiry.pop(key, None)
                    
                    self.logger.info(f"Loaded {len(self.memory_cache)} cached memory items")
            except Exception as e:
                self.logger.error(f"Error loading cached memory data: {str(e)}")
                self.memory_cache = {}
                self.cache_expiry = {}
    
    def _save_cached_data(self):
        """Save cached memory data"""
        cache_path = os.path.join(self.memory_dir, "memory_cache.json")
        try:
            # Clean expired cache entries
            now = time.time()
            for key in list(self.cache_expiry.keys()):
                if self.cache_expiry[key] < now:
                    self.memory_cache.pop(key, None)
                    self.cache_expiry.pop(key, None)
            
            cache_data = {
                'cache': self.memory_cache,
                'expiry': self.cache_expiry,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            self.logger.info(f"Saved {len(self.memory_cache)} cached memory items")
        except Exception as e:
            self.logger.error(f"Error saving cached memory data: {str(e)}")
    
    def store_memory(self, content, memory_type='general', metadata=None, source=None, importance=0.5, expiry=None):
        """
        Store a new memory item
        
        Args:
            content (str): The content of the memory
            memory_type (str): Type of memory (general, conversation, factual, procedural)
            metadata (dict): Additional metadata about the memory
            source (str): Source of the memory (user, system, platform name)
            importance (float): Importance score (0.0-1.0) for prioritization
            expiry (datetime): When the memory should expire (None for no expiry)
            
        Returns:
            int: ID of the stored memory item, or None if failed
        """
        if not self.is_connected:
            self.logger.warning("Database not connected, memory storage disabled")
            return None
            
        if not content or not content.strip():
            self.logger.warning("Empty content provided, memory not stored")
            return None
            
        conn = self._get_db_connection()
        if not conn:
            return None
            
        memory_id = None
        try:
            with conn.cursor() as cursor:
                # Insert the memory item
                cursor.execute("""
                    INSERT INTO memory_items
                    (memory_type, content, metadata, source, importance, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    memory_type,
                    content,
                    json.dumps(metadata) if metadata else None,
                    source,
                    importance,
                    expiry
                ))
                
                memory_id = cursor.fetchone()[0]
                conn.commit()
                
                # Update semantic index
                self._update_memory_embedding(memory_id, content, conn)
                
                self.logger.info(f"Stored new memory item with ID {memory_id}")
                
                # Trigger memory consolidation if needed
                self._maybe_consolidate_memory()
                
                return memory_id
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error storing memory: {str(e)}")
            return None
        finally:
            self._return_db_connection(conn)
    
    def _update_memory_embedding(self, memory_id, content, conn=None):
        """
        Update the vector embedding for a memory item
        
        Args:
            memory_id (int): ID of the memory item
            content (str): Content to embed
            conn: Optional database connection
        """
        if not content or not content.strip():
            return
            
        # For simplicity, we'll use TF-IDF vectors as embeddings
        # In a real system, you'd use more sophisticated embeddings (e.g., from OpenAI)
        
        # Create embedding ID
        embedding_id = f"mem_{memory_id}_{int(time.time())}"
        
        # Get a connection if not provided
        close_conn = False
        if not conn:
            conn = self._get_db_connection()
            close_conn = True
        
        if not conn:
            return
            
        try:
            # Create a simple embedding as a numpy array of floats
            # This is a placeholder - in production you'd use a proper embedding model
            
            # Convert content to vector using the existing vectorizer
            if self.conversation_vectorizer:
                vector = self.conversation_vectorizer.transform([content]).toarray()[0]
                
                # Limit to 100 dimensions for storage efficiency
                vector = vector[:100] if len(vector) > 100 else vector
                
                # Pad with zeros if needed
                if len(vector) < 100:
                    vector = np.pad(vector, (0, 100 - len(vector)))
                
                # Convert to Python list for storage
                vector_list = vector.tolist()
                
                with conn.cursor() as cursor:
                    # Store the embedding
                    cursor.execute("""
                        INSERT INTO vector_embeddings (id, embedding, metadata)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                    """, (
                        embedding_id,
                        vector_list,
                        json.dumps({'memory_id': memory_id, 'content_length': len(content)})
                    ))
                    
                    # Update the memory item with the embedding ID
                    cursor.execute("""
                        UPDATE memory_items
                        SET embedding_id = %s
                        WHERE id = %s
                    """, (embedding_id, memory_id))
                    
                    conn.commit()
                    self.logger.info(f"Updated embedding for memory item {memory_id}")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error updating memory embedding: {str(e)}")
        finally:
            if close_conn:
                self._return_db_connection(conn)
    
    def retrieve_memory(self, query, memory_type=None, limit=5, min_similarity=0.3):
        """
        Retrieve memories semantically similar to the query
        
        Args:
            query (str): The query text to match against memories
            memory_type (str, optional): Filter by memory type
            limit (int): Maximum number of results to return
            min_similarity (float): Minimum similarity score (0.0-1.0)
            
        Returns:
            list: Matching memory items with similarity scores
        """
        # Check cache first
        cache_key = f"query_{hash(query)}_{memory_type}_{limit}_{min_similarity}"
        if cache_key in self.memory_cache and self.cache_expiry.get(cache_key, 0) > time.time():
            return self.memory_cache[cache_key]
            
        if not self.is_connected:
            self.logger.warning("Database not connected, memory retrieval disabled")
            return []
            
        conn = self._get_db_connection()
        if not conn:
            return []
            
        try:
            results = []
            
            if self.conversation_vectorizer and self.conversation_vectors is not None:
                # Convert query to vector
                query_vector = self.conversation_vectorizer.transform([query])
                
                # Calculate similarity with all conversations
                similarities = cosine_similarity(query_vector, self.conversation_vectors).flatten()
                
                # Get top results above minimum similarity
                top_indices = [i for i, sim in enumerate(similarities) if sim >= min_similarity]
                top_indices = sorted(top_indices, key=lambda i: similarities[i], reverse=True)[:limit]
                
                # Get memory items
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    for idx in top_indices:
                        if idx < len(self.conversation_ids):
                            conv_id = self.conversation_ids[idx]
                            
                            # Query for memory items with this conversation ID in metadata
                            cursor.execute("""
                                SELECT id, memory_type, content, metadata, source, importance, 
                                       created_at, expires_at
                                FROM memory_items
                                WHERE metadata->>'conversation_id' = %s
                                  AND (memory_type = %s OR %s IS NULL)
                                ORDER BY importance DESC
                                LIMIT 1
                            """, (str(conv_id), memory_type, memory_type))
                            
                            memory_items = cursor.fetchall()
                            
                            for item in memory_items:
                                # Convert to dict and add similarity score
                                memory_dict = dict(item)
                                memory_dict['similarity'] = float(similarities[idx])
                                
                                # Parse JSON fields
                                if memory_dict['metadata']:
                                    memory_dict['metadata'] = json.loads(memory_dict['metadata'])
                                
                                # Format datetime objects
                                if memory_dict['created_at']:
                                    memory_dict['created_at'] = memory_dict['created_at'].isoformat()
                                if memory_dict['expires_at']:
                                    memory_dict['expires_at'] = memory_dict['expires_at'].isoformat()
                                
                                results.append(memory_dict)
            
            # If not enough results from conversations, search directly in memory items
            if len(results) < limit:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Do a full-text search on content
                    cursor.execute("""
                        SELECT id, memory_type, content, metadata, source, importance, 
                               created_at, expires_at, 
                               ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) as similarity
                        FROM memory_items
                        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', %s)
                          AND (memory_type = %s OR %s IS NULL)
                          AND (expires_at IS NULL OR expires_at > NOW())
                        ORDER BY similarity DESC, importance DESC
                        LIMIT %s
                    """, (query, query, memory_type, memory_type, limit - len(results)))
                    
                    direct_results = cursor.fetchall()
                    
                    for item in direct_results:
                        # Convert to dict
                        memory_dict = dict(item)
                        
                        # Only add if similarity is above threshold
                        if memory_dict['similarity'] >= min_similarity:
                            # Parse JSON fields
                            if memory_dict['metadata']:
                                memory_dict['metadata'] = json.loads(memory_dict['metadata'])
                            
                            # Format datetime objects
                            if memory_dict['created_at']:
                                memory_dict['created_at'] = memory_dict['created_at'].isoformat()
                            if memory_dict['expires_at']:
                                memory_dict['expires_at'] = memory_dict['expires_at'].isoformat()
                            
                            results.append(memory_dict)
            
            # Sort results by similarity
            results = sorted(results, key=lambda x: x.get('similarity', 0), reverse=True)
            
            # Cache results
            self.memory_cache[cache_key] = results
            self.cache_expiry[cache_key] = time.time() + self.cache_max_age
            
            return results
        except Exception as e:
            self.logger.error(f"Error retrieving memories: {str(e)}")
            return []
        finally:
            self._return_db_connection(conn)
    
    def get_memory_by_id(self, memory_id):
        """
        Get a specific memory item by ID
        
        Args:
            memory_id (int): ID of the memory item
            
        Returns:
            dict: Memory item, or None if not found
        """
        # Check cache first
        cache_key = f"memory_{memory_id}"
        if cache_key in self.memory_cache and self.cache_expiry.get(cache_key, 0) > time.time():
            return self.memory_cache[cache_key]
            
        if not self.is_connected:
            self.logger.warning("Database not connected, memory retrieval disabled")
            return None
            
        conn = self._get_db_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, memory_type, content, metadata, source, importance, 
                           created_at, expires_at
                    FROM memory_items
                    WHERE id = %s
                """, (memory_id,))
                
                item = cursor.fetchone()
                
                if not item:
                    return None
                    
                # Convert to dict
                memory_dict = dict(item)
                
                # Parse JSON fields
                if memory_dict['metadata']:
                    memory_dict['metadata'] = json.loads(memory_dict['metadata'])
                
                # Format datetime objects
                if memory_dict['created_at']:
                    memory_dict['created_at'] = memory_dict['created_at'].isoformat()
                if memory_dict['expires_at']:
                    memory_dict['expires_at'] = memory_dict['expires_at'].isoformat()
                
                # Cache the result
                self.memory_cache[cache_key] = memory_dict
                self.cache_expiry[cache_key] = time.time() + self.cache_max_age
                
                return memory_dict
        except Exception as e:
            self.logger.error(f"Error retrieving memory by ID: {str(e)}")
            return None
        finally:
            self._return_db_connection(conn)
    
    def update_memory(self, memory_id, updates):
        """
        Update an existing memory item
        
        Args:
            memory_id (int): ID of the memory to update
            updates (dict): Fields to update (content, metadata, importance, expiry)
            
        Returns:
            bool: Success status
        """
        if not self.is_connected:
            self.logger.warning("Database not connected, memory update disabled")
            return False
            
        conn = self._get_db_connection()
        if not conn:
            return False
            
        try:
            # Build update SQL
            update_parts = []
            params = []
            
            if 'content' in updates:
                update_parts.append("content = %s")
                params.append(updates['content'])
            
            if 'metadata' in updates:
                update_parts.append("metadata = %s")
                params.append(json.dumps(updates['metadata']))
            
            if 'importance' in updates:
                update_parts.append("importance = %s")
                params.append(updates['importance'])
            
            if 'expiry' in updates:
                update_parts.append("expires_at = %s")
                params.append(updates['expiry'])
            
            if not update_parts:
                self.logger.warning("No updates provided for memory item")
                return False
            
            # Add memory_id to params
            params.append(memory_id)
            
            with conn.cursor() as cursor:
                # Update the memory item
                cursor.execute(f"""
                    UPDATE memory_items
                    SET {', '.join(update_parts)}
                    WHERE id = %s
                    RETURNING id
                """, params)
                
                updated_id = cursor.fetchone()
                
                if not updated_id:
                    conn.rollback()
                    self.logger.warning(f"Memory item {memory_id} not found")
                    return False
                
                # If content was updated, update the embedding
                if 'content' in updates:
                    self._update_memory_embedding(memory_id, updates['content'], conn)
                
                conn.commit()
                
                # Clear cache for this memory
                cache_key = f"memory_{memory_id}"
                self.memory_cache.pop(cache_key, None)
                self.cache_expiry.pop(cache_key, None)
                
                self.logger.info(f"Updated memory item {memory_id}")
                return True
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error updating memory: {str(e)}")
            return False
        finally:
            self._return_db_connection(conn)
    
    def delete_memory(self, memory_id):
        """
        Delete a memory item
        
        Args:
            memory_id (int): ID of the memory to delete
            
        Returns:
            bool: Success status
        """
        if not self.is_connected:
            self.logger.warning("Database not connected, memory deletion disabled")
            return False
            
        conn = self._get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                # Delete the memory item
                cursor.execute("""
                    DELETE FROM memory_items
                    WHERE id = %s
                    RETURNING embedding_id
                """, (memory_id,))
                
                result = cursor.fetchone()
                
                if not result:
                    conn.rollback()
                    self.logger.warning(f"Memory item {memory_id} not found")
                    return False
                
                embedding_id = result[0]
                
                # Delete the embedding if it exists
                if embedding_id:
                    cursor.execute("""
                        DELETE FROM vector_embeddings
                        WHERE id = %s
                    """, (embedding_id,))
                
                conn.commit()
                
                # Clear cache for this memory
                cache_key = f"memory_{memory_id}"
                self.memory_cache.pop(cache_key, None)
                self.cache_expiry.pop(cache_key, None)
                
                # Clear query caches as they may contain this memory
                for key in list(self.cache_expiry.keys()):
                    if key.startswith('query_'):
                        self.memory_cache.pop(key, None)
                        self.cache_expiry.pop(key, None)
                
                self.logger.info(f"Deleted memory item {memory_id}")
                return True
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error deleting memory: {str(e)}")
            return False
        finally:
            self._return_db_connection(conn)
    
    def store_context(self, context_name, context_data, metadata=None, source=None, priority=0.5):
        """
        Store a memory context (for context-aware retrieval)
        
        Args:
            context_name (str): Name/identifier for the context
            context_data (dict): Context data
            metadata (dict, optional): Additional metadata about the context
            source (str, optional): Source of the context (user, system, platform name)
            priority (float, optional): Priority score (0.0-1.0) for context importance
            
        Returns:
            int: Context ID, or None if failed
        """
        if not self.is_connected:
            self.logger.warning("Database not connected, context storage disabled")
            return None
            
        conn = self._get_db_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor() as cursor:
                # Check if context already exists
                cursor.execute("""
                    SELECT id FROM memory_contexts
                    WHERE context_name = %s
                """, (context_name,))
                
                existing = cursor.fetchone()
                
                # Add version tracking for context history
                version = 1
                
                # Prepare metadata with enhanced tracking
                enhanced_metadata = metadata or {}
                
                # Add source information if provided
                if source:
                    enhanced_metadata['source'] = source
                
                # Add context tracking information
                enhanced_metadata['priority'] = priority
                enhanced_metadata['accessed_count'] = 0
                enhanced_metadata['last_accessed'] = None
                
                if existing:
                    # Get existing metadata to update version
                    cursor.execute("""
                        SELECT context_data, context_name FROM memory_contexts
                        WHERE id = %s
                    """, (existing[0],))
                    
                    existing_data = cursor.fetchone()
                    if existing_data and existing_data[0]:
                        try:
                            existing_json = json.loads(existing_data[0])
                            existing_meta = existing_json.get('_metadata', {})
                            version = existing_meta.get('version', 0) + 1
                            
                            # Preserve access count if it exists
                            if 'accessed_count' in existing_meta:
                                enhanced_metadata['accessed_count'] = existing_meta['accessed_count']
                            
                            # Preserve last accessed timestamp if it exists
                            if 'last_accessed' in existing_meta:
                                enhanced_metadata['last_accessed'] = existing_meta['last_accessed']
                        except Exception as json_err:
                            self.logger.warning(f"Error parsing existing context metadata: {str(json_err)}")
                    
                    # Update existing context with version tracking
                    enhanced_metadata['version'] = version
                    enhanced_metadata['updated_at'] = datetime.datetime.now().isoformat()
                    
                    # Add metadata to context data
                    context_data_with_meta = {
                        'data': context_data,
                        '_metadata': enhanced_metadata
                    }
                    
                    cursor.execute("""
                        UPDATE memory_contexts
                        SET context_data = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING id
                    """, (json.dumps(context_data_with_meta), existing[0]))
                    
                    context_id = cursor.fetchone()[0]
                    self.logger.info(f"Updated context {context_name} (version {version}) with ID {context_id}")
                else:
                    # Initialize metadata for new context
                    enhanced_metadata['version'] = version
                    enhanced_metadata['created_at'] = datetime.datetime.now().isoformat()
                    enhanced_metadata['updated_at'] = datetime.datetime.now().isoformat()
                    
                    # Add metadata to context data
                    context_data_with_meta = {
                        'data': context_data,
                        '_metadata': enhanced_metadata
                    }
                    
                    # Insert new context
                    cursor.execute("""
                        INSERT INTO memory_contexts
                        (context_name, context_data)
                        VALUES (%s, %s)
                        RETURNING id
                    """, (context_name, json.dumps(context_data_with_meta)))
                    
                    context_id = cursor.fetchone()[0]
                    self.logger.info(f"Created new context {context_name} (version {version}) with ID {context_id}")
                
                conn.commit()
                
                # Add the context to the memory links graph if enabled
                if context_id and context_data.get('related_memories'):
                    self._link_context_to_memories(conn, context_id, context_data.get('related_memories'))
                
                return context_id
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error storing context: {str(e)}")
            return None
        finally:
            self._return_db_connection(conn)
            
    def _link_context_to_memories(self, conn, context_id, memory_ids):
        """
        Create links between a context and related memories
        
        Args:
            conn: Database connection
            context_id (int): ID of the context
            memory_ids (list): List of memory IDs to link to the context
        """
        if not memory_ids or not isinstance(memory_ids, list):
            return
            
        try:
            with conn.cursor() as cursor:
                # Create links for each memory ID
                for memory_id in memory_ids:
                    # Skip invalid IDs
                    if not memory_id:
                        continue
                        
                    # Create a link using memory_links table
                    cursor.execute("""
                        INSERT INTO memory_links
                        (source_id, target_id, link_type, weight)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (memory_id, context_id, 'context_association', 0.8))
                    
            conn.commit()
            self.logger.info(f"Linked context {context_id} to {len(memory_ids)} memories")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error linking context to memories: {str(e)}")
    
    def get_context(self, context_name):
        """
        Get a memory context by name
        
        Args:
            context_name (str): Name/identifier for the context
            
        Returns:
            dict: Context data, or None if not found
        """
        if not self.is_connected:
            self.logger.warning("Database not connected, context retrieval disabled")
            return None
            
        conn = self._get_db_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, context_name, context_data, created_at, updated_at
                    FROM memory_contexts
                    WHERE context_name = %s
                """, (context_name,))
                
                context = cursor.fetchone()
                
                if not context:
                    return None
                    
                # Convert to dict
                context_dict = dict(context)
                
                # Parse JSON fields
                if context_dict['context_data']:
                    context_dict['context_data'] = json.loads(context_dict['context_data'])
                
                # Format datetime objects
                if context_dict['created_at']:
                    context_dict['created_at'] = context_dict['created_at'].isoformat()
                if context_dict['updated_at']:
                    context_dict['updated_at'] = context_dict['updated_at'].isoformat()
                
                return context_dict
        except Exception as e:
            self.logger.error(f"Error retrieving context: {str(e)}")
            return None
        finally:
            self._return_db_connection(conn)
    
    def retrieve_with_context(self, query, context_name, memory_type=None, limit=5, min_similarity=0.3):
        """
        Retrieve memories with context-awareness
        
        Args:
            query (str): The query text to match against memories
            context_name (str): Name of the context to consider
            memory_type (str, optional): Filter by memory type
            limit (int): Maximum number of results to return
            min_similarity (float): Minimum similarity score (0.0-1.0)
            
        Returns:
            list: Matching memory items with similarity scores
        """
        # First get the context
        context = self.get_context(context_name)
        
        if not context or not context.get('context_data'):
            # Fallback to regular retrieval if context not found
            return self.retrieve_memory(query, memory_type, limit, min_similarity)
        
        # Enhance query with context information
        context_data = context['context_data']
        
        # Add context terms to query if available
        enhanced_query = query
        
        if 'focus' in context_data:
            enhanced_query += f" {context_data['focus']}"
            
        if 'recent_topics' in context_data and isinstance(context_data['recent_topics'], list):
            enhanced_query += f" {' '.join(context_data['recent_topics'][:3])}"
        
        # Retrieve memories with enhanced query
        results = self.retrieve_memory(enhanced_query, memory_type, limit * 2, min_similarity)
        
        # Re-rank results based on context relevance
        for result in results:
            # Base score is the similarity score
            context_score = result.get('similarity', 0)
            
            # Boost score based on context relevance
            metadata = result.get('metadata', {})
            
            # Boost based on topic match
            if 'topic' in metadata and 'preferred_topics' in context_data:
                if metadata['topic'] in context_data['preferred_topics']:
                    context_score += 0.2
            
            # Boost based on recency if context has recency preference
            if 'created_at' in result and context_data.get('recency_preference', False):
                # Parse timestamp
                try:
                    created_dt = datetime.datetime.fromisoformat(result['created_at'].replace('Z', '+00:00'))
                    now = datetime.datetime.now()
                    age_days = (now - created_dt).total_seconds() / (24 * 3600)
                    
                    # Boost more recent items (max 0.1 boost for items less than a day old)
                    recency_boost = max(0, 0.1 - (age_days * 0.01))
                    context_score += recency_boost
                except:
                    pass
            
            # Boost based on importance if context has importance preference
            if 'importance' in result and context_data.get('importance_preference', False):
                importance_boost = result['importance'] * 0.2
                context_score += importance_boost
            
            # Update the result's score
            result['context_score'] = min(1.0, context_score)
        
        # Sort by context score and limit results
        results = sorted(results, key=lambda x: x.get('context_score', 0), reverse=True)
        return results[:limit]
    
    def create_memory_link(self, source_id, target_id, link_type='associated', weight=0.5):
        """
        Create a link between memory items
        
        Args:
            source_id (int): ID of the source memory
            target_id (int): ID of the target memory
            link_type (str): Type of link (associated, causal, sequential)
            weight (float): Link weight/strength (0.0-1.0)
            
        Returns:
            int: Link ID, or None if failed
        """
        if not self.is_connected:
            self.logger.warning("Database not connected, memory linking disabled")
            return None
            
        conn = self._get_db_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor() as cursor:
                # Check if both memory items exist
                cursor.execute("""
                    SELECT id FROM memory_items WHERE id IN (%s, %s)
                """, (source_id, target_id))
                
                found_ids = cursor.fetchall()
                if len(found_ids) < 2:
                    self.logger.warning(f"Cannot create link: one or both memory items not found")
                    return None
                
                # Check if link already exists
                cursor.execute("""
                    SELECT id FROM memory_links
                    WHERE source_id = %s AND target_id = %s
                """, (source_id, target_id))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing link
                    cursor.execute("""
                        UPDATE memory_links
                        SET link_type = %s, weight = %s
                        WHERE id = %s
                        RETURNING id
                    """, (link_type, weight, existing[0]))
                    
                    link_id = cursor.fetchone()[0]
                else:
                    # Insert new link
                    cursor.execute("""
                        INSERT INTO memory_links
                        (source_id, target_id, link_type, weight)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (source_id, target_id, link_type, weight))
                    
                    link_id = cursor.fetchone()[0]
                
                conn.commit()
                self.logger.info(f"Created memory link {link_id} between {source_id} and {target_id}")
                return link_id
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error creating memory link: {str(e)}")
            return None
        finally:
            self._return_db_connection(conn)
    
    def get_linked_memories(self, memory_id, link_type=None, min_weight=0.0):
        """
        Get memories linked to a specific memory
        
        Args:
            memory_id (int): ID of the memory
            link_type (str, optional): Filter by link type
            min_weight (float): Minimum link weight
            
        Returns:
            list: Linked memory items with link metadata
        """
        if not self.is_connected:
            self.logger.warning("Database not connected, linked memory retrieval disabled")
            return []
            
        conn = self._get_db_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # First get outgoing links
                cursor.execute("""
                    SELECT m.id, m.memory_type, m.content, m.metadata, 
                           m.source, m.importance, m.created_at,
                           l.link_type, l.weight, 'outgoing' as direction
                    FROM memory_links l
                    JOIN memory_items m ON l.target_id = m.id
                    WHERE l.source_id = %s
                      AND (l.link_type = %s OR %s IS NULL)
                      AND l.weight >= %s
                """, (memory_id, link_type, link_type, min_weight))
                
                outgoing = cursor.fetchall()
                
                # Then get incoming links
                cursor.execute("""
                    SELECT m.id, m.memory_type, m.content, m.metadata, 
                           m.source, m.importance, m.created_at,
                           l.link_type, l.weight, 'incoming' as direction
                    FROM memory_links l
                    JOIN memory_items m ON l.source_id = m.id
                    WHERE l.target_id = %s
                      AND (l.link_type = %s OR %s IS NULL)
                      AND l.weight >= %s
                """, (memory_id, link_type, link_type, min_weight))
                
                incoming = cursor.fetchall()
                
                # Combine results
                results = []
                
                for item in outgoing + incoming:
                    # Convert to dict
                    memory_dict = dict(item)
                    
                    # Parse JSON fields
                    if memory_dict['metadata']:
                        memory_dict['metadata'] = json.loads(memory_dict['metadata'])
                    
                    # Format datetime objects
                    if memory_dict['created_at']:
                        memory_dict['created_at'] = memory_dict['created_at'].isoformat()
                    
                    results.append(memory_dict)
                
                return results
        except Exception as e:
            self.logger.error(f"Error retrieving linked memories: {str(e)}")
            return []
        finally:
            self._return_db_connection(conn)
    
    def _maybe_consolidate_memory(self, force=False):
        """
        Check if memory consolidation should be performed and do it if needed
        
        Args:
            force (bool): Force consolidation regardless of thresholds
            
        Returns:
            bool: Whether consolidation was performed
        """
        # Simple criteria - consolidate based on number of unconsolidated items
        if not self.is_connected:
            return False
            
        # To avoid constant DB checks, use a random chance unless forced
        if not force and random.random() > 0.1:  # 10% chance on regular operations
            return False
            
        conn = self._get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                # Count unconsolidated items
                cursor.execute("""
                    SELECT COUNT(*) FROM memory_items
                    WHERE is_consolidated = FALSE
                """)
                
                count = cursor.fetchone()[0]
                
                # Consolidate if count exceeds threshold or if forced
                threshold = 20  # Adjust based on performance needs
                if count >= threshold or force:
                    self.logger.info(f"Starting memory consolidation for {count} items")
                    consolidation_result = self._consolidate_memory(conn)
                    
                    if consolidation_result:
                        self.logger.info(f"Memory consolidation complete: {consolidation_result}")
                        return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error in memory consolidation check: {str(e)}")
            return False
        finally:
            self._return_db_connection(conn)
    
    def _consolidate_memory(self, conn=None):
        """
        Perform memory consolidation to extract and store higher-level knowledge
        
        Args:
            conn: Optional database connection
            
        Returns:
            dict: Consolidation results
        """
        # Get a connection if not provided
        close_conn = False
        if not conn:
            conn = self._get_db_connection()
            close_conn = True
        
        if not conn:
            return None
            
        try:
            # Group unconsolidated memories by type
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT memory_type, array_agg(id) as ids, array_agg(content) as contents
                    FROM memory_items
                    WHERE is_consolidated = FALSE
                    GROUP BY memory_type
                """)
                
                memory_groups = cursor.fetchall()
            
            results = {
                'consolidated_count': 0,
                'knowledge_created': 0,
                'areas': []
            }
            
            for group in memory_groups:
                memory_type = group['memory_type']
                memory_ids = group['ids']
                memory_contents = group['contents']
                
                if not memory_ids or len(memory_ids) < 2:
                    continue
                
                # For each group, identify knowledge areas
                knowledge_areas = self._identify_knowledge_areas(memory_contents)
                
                # For each knowledge area, consolidate memories
                for area, area_info in knowledge_areas.items():
                    related_ids = []
                    
                    # Create consolidated knowledge
                    summary = area_info.get('summary', f"Consolidated knowledge about {area}")
                    confidence = area_info.get('confidence', 0.7)
                    
                    # Store in consolidated_knowledge table
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO consolidated_knowledge
                            (knowledge_area, content, source_ids, confidence)
                            VALUES (%s, %s, %s, %s)
                            RETURNING id
                        """, (area, summary, memory_ids, confidence))
                        
                        knowledge_id = cursor.fetchone()[0]
                        
                        # Mark memories as consolidated
                        cursor.execute("""
                            UPDATE memory_items
                            SET is_consolidated = TRUE
                            WHERE id = ANY(%s)
                        """, (memory_ids,))
                        
                        conn.commit()
                        
                        results['consolidated_count'] += len(memory_ids)
                        results['knowledge_created'] += 1
                        results['areas'].append(area)
            
            return results
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Error in memory consolidation: {str(e)}")
            return None
        finally:
            if close_conn and conn:
                self._return_db_connection(conn)
    
    def _identify_knowledge_areas(self, contents):
        """
        Identify knowledge areas from memory contents
        
        Args:
            contents (list): List of memory content strings
            
        Returns:
            dict: Identified knowledge areas with metadata
        """
        # This is a simplified implementation
        # In a real system, this would use NLP to identify topics and extract knowledge
        
        # Join all contents
        all_content = " ".join(contents)
        
        # Simple keyword extraction
        words = all_content.lower().split()
        word_freq = {}
        
        # Skip common words
        stop_words = set(['the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Create a simple summary
        keywords = [k for k, v in top_keywords]
        sample_content = contents[0][:100] + "..." if contents else ""
        
        # Create a knowledge area for each top keyword
        knowledge_areas = {}
        
        for keyword, freq in top_keywords:
            if freq >= 2:  # Only consider keywords that appear multiple times
                knowledge_areas[keyword] = {
                    'summary': f"Knowledge about {keyword} extracted from {len(contents)} memories: {sample_content}",
                    'confidence': min(0.9, 0.5 + (freq / 10)),
                    'frequency': freq
                }
        
        return knowledge_areas
    
    def get_consolidated_knowledge(self, area=None, min_confidence=0.5, limit=10):
        """
        Get consolidated knowledge from memory
        
        Args:
            area (str, optional): Filter by knowledge area
            min_confidence (float): Minimum confidence score
            limit (int): Maximum number of results
            
        Returns:
            list: Consolidated knowledge items
        """
        if not self.is_connected:
            self.logger.warning("Database not connected, knowledge retrieval disabled")
            return []
            
        conn = self._get_db_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Query for consolidated knowledge
                if area:
                    cursor.execute("""
                        SELECT id, knowledge_area, content, source_ids, confidence, 
                               created_at, updated_at
                        FROM consolidated_knowledge
                        WHERE knowledge_area = %s
                          AND confidence >= %s
                        ORDER BY confidence DESC, updated_at DESC
                        LIMIT %s
                    """, (area, min_confidence, limit))
                else:
                    cursor.execute("""
                        SELECT id, knowledge_area, content, source_ids, confidence, 
                               created_at, updated_at
                        FROM consolidated_knowledge
                        WHERE confidence >= %s
                        ORDER BY confidence DESC, updated_at DESC
                        LIMIT %s
                    """, (min_confidence, limit))
                
                items = cursor.fetchall()
                
                results = []
                for item in items:
                    # Convert to dict
                    knowledge_dict = dict(item)
                    
                    # Format datetime objects
                    if knowledge_dict['created_at']:
                        knowledge_dict['created_at'] = knowledge_dict['created_at'].isoformat()
                    if knowledge_dict['updated_at']:
                        knowledge_dict['updated_at'] = knowledge_dict['updated_at'].isoformat()
                    
                    results.append(knowledge_dict)
                
                return results
        except Exception as e:
            self.logger.error(f"Error retrieving consolidated knowledge: {str(e)}")
            return []
        finally:
            self._return_db_connection(conn)
    
    def store_conversation_summary(self, conversation_id, summary, key_points=None, topic=None):
        """
        Store a summary of a conversation for improved memory recall
        
        Args:
            conversation_id: ID of the conversation
            summary (str): Summary text
            key_points (list, optional): Key points extracted from the conversation
            topic (str, optional): Topic of the conversation
            
        Returns:
            int: ID of the stored memory, or None if failed
        """
        # Create metadata
        metadata = {
            'conversation_id': conversation_id,
            'content_type': 'summary'
        }
        
        if key_points:
            metadata['key_points'] = key_points
            
        if topic:
            metadata['topic'] = topic
        
        # Store as a memory item
        memory_id = self.store_memory(
            content=summary,
            memory_type='conversation_summary',
            metadata=metadata,
            source='system',
            importance=0.8  # Summaries are important for recall
        )
        
        return memory_id
    
    def find_conversation_summaries(self, topic=None, limit=5):
        """
        Find conversation summaries, optionally filtered by topic
        
        Args:
            topic (str, optional): Topic to filter by
            limit (int): Maximum number of results
            
        Returns:
            list: Matching summaries
        """
        if not self.is_connected:
            self.logger.warning("Database not connected, summary retrieval disabled")
            return []
            
        conn = self._get_db_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if topic:
                    cursor.execute("""
                        SELECT id, content, metadata, importance, created_at
                        FROM memory_items
                        WHERE memory_type = 'conversation_summary'
                          AND metadata->>'topic' = %s
                        ORDER BY importance DESC, created_at DESC
                        LIMIT %s
                    """, (topic, limit))
                else:
                    cursor.execute("""
                        SELECT id, content, metadata, importance, created_at
                        FROM memory_items
                        WHERE memory_type = 'conversation_summary'
                        ORDER BY importance DESC, created_at DESC
                        LIMIT %s
                    """, (limit,))
                
                items = cursor.fetchall()
                
                results = []
                for item in items:
                    # Convert to dict
                    summary_dict = dict(item)
                    
                    # Parse JSON fields
                    if summary_dict['metadata']:
                        summary_dict['metadata'] = json.loads(summary_dict['metadata'])
                    
                    # Format datetime objects
                    if summary_dict['created_at']:
                        summary_dict['created_at'] = summary_dict['created_at'].isoformat()
                    
                    results.append(summary_dict)
                
                return results
        except Exception as e:
            self.logger.error(f"Error retrieving conversation summaries: {str(e)}")
            return []
        finally:
            self._return_db_connection(conn)
    
    def synchronize_with_base_memory(self):
        """
        Synchronize with the base memory system
        
        Pulls new conversations and threads from the base memory system
        and adds them to the advanced memory system
        
        Returns:
            dict: Synchronization results
        """
        if not self.base_memory_system:
            self.logger.warning("Base memory system not available, synchronization disabled")
            return {'status': 'error', 'message': 'Base memory system not available'}
        
        results = {
            'status': 'success',
            'conversations_synced': 0,
            'threads_synced': 0,
            'memories_created': 0
        }
        
        try:
            # Get conversations from base memory
            conversations = self.base_memory_system.get_conversations(limit=100)
            
            if conversations:
                for conv in conversations:
                    conv_id = conv.get('id')
                    
                    # Skip if we've already processed this conversation
                    if self._check_conversation_synced(conv_id):
                        continue
                    
                    # Create a memory item for the conversation
                    # Combine messages into a single text
                    messages = [f"{'User' if msg.get('is_user') else 'AI'}: {msg.get('content', '')}" 
                               for msg in conv.get('messages', [])]
                    content = "\n".join(messages)
                    
                    if content.strip():
                        # Store as memory
                        metadata = {
                            'conversation_id': conv_id,
                            'platform': conv.get('platform'),
                            'subject': conv.get('subject'),
                            'goal': conv.get('goal'),
                            'messages_count': len(conv.get('messages', []))
                        }
                        
                        memory_id = self.store_memory(
                            content=content,
                            memory_type='conversation',
                            metadata=metadata,
                            source=conv.get('platform'),
                            importance=0.6
                        )
                        
                        if memory_id:
                            results['memories_created'] += 1
                            
                            # Generate and store a summary if the conversation is substantial
                            if len(conv.get('messages', [])) >= 3:
                                summary = self._generate_summary(content)
                                if summary:
                                    summary_id = self.store_conversation_summary(
                                        conversation_id=conv_id,
                                        summary=summary,
                                        topic=conv.get('subject')
                                    )
                                    if summary_id:
                                        results['memories_created'] += 1
                        
                    results['conversations_synced'] += 1
            
            # Get threads from base memory
            threads = self.base_memory_system.get_threads(limit=50)
            
            if threads:
                for thread in threads:
                    thread_id = thread.get('id')
                    
                    # Skip if we've already processed this thread
                    if self._check_thread_synced(thread_id):
                        continue
                    
                    # Create a memory item for the thread
                    content = f"Training Thread: {thread.get('subject')}\n\nGoal: {thread.get('goal')}\n\n"
                    
                    if thread.get('final_plan'):
                        content += f"Final Plan: {thread.get('final_plan')}\n\n"
                    
                    if thread.get('ai_contributions'):
                        content += "AI Contributions:\n"
                        for platform, contributions in thread.get('ai_contributions', {}).items():
                            content += f"{platform}: {contributions}\n"
                    
                    if content.strip():
                        # Store as memory
                        metadata = {
                            'thread_id': thread_id,
                            'subject': thread.get('subject'),
                            'goal': thread.get('goal'),
                            'conversations': [c.get('id') for c in thread.get('conversations', [])]
                        }
                        
                        memory_id = self.store_memory(
                            content=content,
                            memory_type='thread',
                            metadata=metadata,
                            source='system',
                            importance=0.7
                        )
                        
                        if memory_id:
                            results['memories_created'] += 1
                        
                    results['threads_synced'] += 1
            
            # Update semantic index with new data
            self._update_semantic_index()
            
            return results
        except Exception as e:
            self.logger.error(f"Error synchronizing with base memory: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _check_conversation_synced(self, conversation_id):
        """Check if a conversation has already been synced"""
        if not self.is_connected:
            return False
            
        conn = self._get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM memory_items
                    WHERE metadata->>'conversation_id' = %s
                """, (str(conversation_id),))
                
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            self.logger.error(f"Error checking conversation sync status: {str(e)}")
            return False
        finally:
            self._return_db_connection(conn)
    
    def _check_thread_synced(self, thread_id):
        """Check if a thread has already been synced"""
        if not self.is_connected:
            return False
            
        conn = self._get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM memory_items
                    WHERE metadata->>'thread_id' = %s
                """, (str(thread_id),))
                
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            self.logger.error(f"Error checking thread sync status: {str(e)}")
            return False
        finally:
            self._return_db_connection(conn)
    
    def _generate_summary(self, content):
        """Generate a summary of content"""
        # This is a simplified implementation
        # In a real system, this would use an LLM or summarization algorithm
        
        if not content or len(content) < 100:
            return None
            
        # Simple extractive summarization
        sentences = content.split('.')
        
        if len(sentences) <= 3:
            return content
            
        # Take first sentence, a middle sentence, and last sentence
        summary = f"{sentences[0].strip()}. "
        
        middle_idx = len(sentences) // 2
        if middle_idx > 0 and middle_idx < len(sentences):
            summary += f"{sentences[middle_idx].strip()}. "
            
        if len(sentences) > 2:
            summary += f"{sentences[-2].strip()}."
            
        return summary
    
    def optimize_storage(self):
        """
        Optimize memory storage by cleaning up old or unimportant memories
        
        Returns:
            dict: Optimization results
        """
        if not self.is_connected:
            self.logger.warning("Database not connected, storage optimization disabled")
            return {'status': 'error', 'message': 'Database not connected'}
            
        conn = self._get_db_connection()
        if not conn:
            return {'status': 'error', 'message': 'Could not get database connection'}
            
        try:
            results = {
                'status': 'success',
                'expired_deleted': 0,
                'unimportant_deleted': 0,
                'storage_reclaimed': 0
            }
            
            with conn.cursor() as cursor:
                # Delete expired memories
                cursor.execute("""
                    DELETE FROM memory_items
                    WHERE expires_at IS NOT NULL AND expires_at < NOW()
                    RETURNING id
                """)
                
                expired_ids = cursor.fetchall()
                results['expired_deleted'] = len(expired_ids)
                
                # Delete unimportant, old memories
                # (low importance, old, and already consolidated)
                cursor.execute("""
                    DELETE FROM memory_items
                    WHERE importance < 0.3
                      AND created_at < NOW() - INTERVAL '30 days'
                      AND is_consolidated = TRUE
                    RETURNING id
                """)
                
                unimportant_ids = cursor.fetchall()
                results['unimportant_deleted'] = len(unimportant_ids)
                
                # Estimate storage reclaimed
                cursor.execute("SELECT pg_database_size(current_database())")
                before_size = cursor.fetchone()[0]
                
                conn.commit()
                
                # Vacuum the database to reclaim space
                cursor.execute("VACUUM")
                
                # Check size after optimization
                cursor.execute("SELECT pg_database_size(current_database())")
                after_size = cursor.fetchone()[0]
                
                results['storage_reclaimed'] = before_size - after_size
                
                self.logger.info(f"Storage optimization complete: {results}")
                return results
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error optimizing storage: {str(e)}")
            return {'status': 'error', 'message': str(e)}
        finally:
            self._return_db_connection(conn)
    
    def __del__(self):
        """Clean up resources on deletion"""
        # Save cached data before shutting down
        self._save_cached_data()
        
        # Close all database connections
        if self.connection_pool:
            self.connection_pool.closeall()
            self.logger.info("Closed all database connections")