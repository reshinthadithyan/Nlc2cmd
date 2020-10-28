from torch.nn import Module
from torch import tensor,uint8,LongTensor,Tensor
from torch.utils.data import DataLoader
from data import OmnibashDataset
from transformers import OpenAIGPTLMHeadModel,OpenAIGPTConfig,GPT2TokenizerFast
from torch import nonzero
class OmniBash(Module):
    def __init__(self,Transformer,Device):
        super(OmniBash,self).__init__()
        self.Trans = Transformer # Transformer ModelEE
        self.device = Device
    def forward(self,Input,Label):
        attn_mask = tensor(Label.clone().detach() != 0.0,dtype=uint8,device=self.device)#.unsqueeze(0) #device=self.device)
        loss_mask = tensor(Label.clone().detach() == 2.0, dtype=uint8,device=self.device)#.unsqueeze(0) #device=self.device)
        Input = Input.long()
        Output = self.Trans(Input,attention_mask=attn_mask)
        logits = Output[0]
        labels = Input
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        flatten_shift_loss_mask = loss_mask[..., :-1].contiguous().view(-1)
        ids = nonzero(flatten_shift_loss_mask).view(-1)
        fin_logits,fin_labels = shift_logits.view(-1, shift_logits.size(-1))[ids], shift_labels.view(-1)[ids]
        return fin_logits,fin_labels

if __name__ == "__main__":
    Trans_Config = OpenAIGPTConfig(vocab_size=3002,n_layer=12)
    Trans_Model = OpenAIGPTLMHeadModel(Trans_Config)
    Token_Dir = r"G:\Work Related\Nlc2cmd\Tokenizer_Train\GPTToken/"
    Trans_Tok = GPT2TokenizerFast.from_pretrained(Token_Dir)
    Omni = OmniBash(Trans_Model,"cpu")
    Dataset = OmnibashDataset(r"G:\Work Related\Nlc2cmd\Data\Template.json",Trans_Tok,"train",100)
    TrainLoader = DataLoader(Dataset,batch_size=10)
    Samples = TrainLoader
    c = 0
    from torch.nn import CrossEntropyLoss
    for step, batch in enumerate(TrainLoader):
        print(c)
        
        x,y = Omni(batch[0],batch[1])
        print(CrossEntropyLoss()(x,y))
        c += 1
        print(x.size())
        print(y.size())