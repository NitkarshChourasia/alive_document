ER - Diagram

```mermaid
  Document {
    string name
    string content
    int size
    string format
  }
  Model {
    string name
    string type
    string source
  }
  Embedding {
    string name
    string type
    string source
  }
  LLM {
    string name
    string type
    string source
  }
  Vector {
    string name
    int dimension
    float[] values
  }
  User {
    string username
    string password
    string email
  }
  Document ||--|{ Model : uses
  Document ||--|{ Embedding : uses
  Document ||--|{ LLM : uses
  Document ||--|{ Vector : has
  Model ||--|{ Embedding : uses
  Model ||--|{ LLM : uses
  Model ||--|{ Vector : has
  Embedding ||--|{ Vector : has
  LLM ||--|{ Vector : has
  User ||--o{ Document : creates
```