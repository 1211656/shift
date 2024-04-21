from main import db


class Password(db.TypeDecorator):
    impl = db.String(80)

    def _set_parent_with_dispatch(self, parent):
        return Password(self.impl._set_parent_with_dispatch(parent))

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.value

    def process_result_value(self, value, dialect):
        if value is not None:
            return Password(value)