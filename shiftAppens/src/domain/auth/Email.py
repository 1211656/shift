from main import db


class Email(db.TypeDecorator):
    impl = db.String(120)

    def _set_parent_with_dispatch(self, parent):
        return Email(self.impl._set_parent_with_dispatch(parent))

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.value

    def process_result_value(self, value, dialect):
        if value is not None:
            return Email(value)
