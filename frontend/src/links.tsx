import {
  Create,
  Datagrid,
  DeleteButton,
  Edit,
  EditButton,
  List,
  required,
  SimpleForm,
  TextField,
  TextInput,
  UrlField,
} from "react-admin";

const LinkForm = () => (
  <SimpleForm>
    <TextInput source="original_url" fullWidth validate={[required()]} />
    <TextInput source="short_name" fullWidth validate={[required()]} />
  </SimpleForm>
);

export const LinkList = () => (
  <List>
    <Datagrid>
      <TextField source="id" />
      <TextField source="short_name" />
      <UrlField source="original_url" target="_blank" />
      <UrlField source="short_url" target="_blank" />
      <EditButton />
      <DeleteButton />
    </Datagrid>
  </List>
);

export const LinkCreate = () => (
  <Create redirect="list">
    <LinkForm />
  </Create>
);

export const LinkEdit = () => (
  <Edit redirect="list">
    <LinkForm />
  </Edit>
);
