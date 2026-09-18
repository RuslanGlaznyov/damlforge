
struct Box:
    holding: ContractId[Party]
    maybe: Optional[Party]
    items: list[Party]
    pair: tuple[Party, Text]
    values: TextMap[Text]
    mapping: GenMap[Text, Int]
